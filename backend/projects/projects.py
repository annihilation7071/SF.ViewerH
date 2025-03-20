from backend.main_import import *
from . import projects_utils
from . import editor

# from backend import dep
# from backend.db import Project
# from backend.classes.lib import Lib
# from sqlalchemy import desc, and_, func, or_, Sequence, not_
# from collections import defaultdict
# from backend.editor import variants_editor
# from backend.utils import *
# from icecream import ic
# from backend import logger
# from sqlalchemy.orm import Session
# from sqlalchemy import select, delete, update
# from backend.projects import projects_utils
# from backend.editor import selector
# from backend.filesession import FileSession, FSession


log = logger.get_logger("Projects.projects")


class ProjectsError(Exception):
    pass


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self):
        log.debug("load projects...")
        log.debug(f"Libs: {dep.libs}")
        self.libs = utils.read_libs(only_active=True, check=True)

        self.all_projects_filter = Project.lib.in_(dep.libs)
        self.all_projects = select(Project).where(self.all_projects_filter)

        self.active_projects_filter = and_(self.all_projects_filter, Project.active == 1)
        self.active_projects = select(Project).where(self.active_projects_filter)

        self.sorting_method = Project.upload_date
        self.search = ""

        self.projects_filter = self.active_projects_filter
        self.projects = select(Project).where(self.projects_filter).order_by(desc(self.sorting_method))

        with dep.Session() as session:
            result = session.scalars(self.projects).all()
            log.info(f"result: {len(result)}")

        log.debug("projects loaded")

    def _normalize_search(self, search: str) -> str:
        search = search.split(",")
        search = [item.strip().lower().replace("\r", "").replace("\n", "").replace("_", " ").strip() for item in search]
        search = ",".join(search)
        return search

    def _filter(self, search: str | None):
        search = self._normalize_search(search)

        if self.search == search:
            return

        if search is None or search == "":
            self.search = ""
            self.projects_filter = self.active_projects_filter
            self.projects = select(Project).where(self.projects_filter).order_by(desc(self.sorting_method))
            return

        def f(item: str):
            if item.find(":") > -1:
                return f";;;{item};;;"
            else:
                return item

        self.search = search
        search = search.split(",")
        search_query = [Project.search_body.icontains(f(item)) for item in search]

        self.projects_filter = and_(self.active_projects_filter, *search_query)
        self.projects = select(Project).where(self.projects_filter).order_by(desc(self.sorting_method))

    def select_sorting_method(self, method: str):
        available = {"upload_date", "preview_hash"}
        if method in available:
            self.sorting_method = getattr(Project, method)
            self.projects = self.projects.order_by(None).order_by(desc(self.sorting_method))
            log.info(f"Sorting method {method} selected")
        else:
            raise ProjectsError(f"Method {method} not supported")

    def get_page(self, ppg: int, page: int = 1, search: str = None):
        self._filter(search)

        with dep.Session() as session, FileSession() as fs:
            projects = session.scalars(self.projects.offset(((page - 1) * ppg)).limit(ppg)).all()

        return projects

    def len(self):
        with dep.Session() as session:
            stmt = select(func.count(Project.lid)).where(self.projects_filter)
            return session.scalar(stmt)

    def renew(self):
        with dep.Session() as session, FileSession() as fs:
            self.update_pools_(session)
            # self.update_aliases_(session, fs)
            session.commit()
            fs.commit()

    def get_project(self, lid: str) -> Project:
        log.debug("get_project")
        with dep.Session() as session, FileSession() as fs:
            # Plus update preview and pages count
            project = Project.project_load_from_db(session, lid)
            # TODO
            # session.commit()
            # fs.commit()
            return project

    def check_project(self, site: str, id_: str | int):
        id_ = str(id_)

        with dep.Session() as session:
            flt = (
                Project.source == site,
                Project.source_id == int(id_),
            )

            stmt = select(func.count(Project.lid)).where(*flt)

            return session.scalar(stmt)

    def update_projects(self):
        with dep.Session() as session, FileSession() as fs:
            projects_utils.update_projects(session, fs)
            session.commit()
            fs.commit()

    def count_item(self, item_: str) -> list:
        log.debug(f"count_item: {item_}")
        result = defaultdict(int)

        with dep.Session() as session:
            projects_ = session.scalars(self.active_projects).all()

            for project in projects_:
                items = getattr(project, item_)
                for item in items:
                    result[item] += 1

        return sorted(result.items(), key=lambda x: x[1], reverse=True)

    def edit(self, project: Project, edit_type: str, data: str):
        with dep.Session() as session, FileSession() as fs:
            result = editor.edit(session, fs, project, edit_type, data)
            session.commit()
            fs.commit()
            return result

    def clear_old_versions_(self, session: Session, target_version: int):
        log.debug(f"clear_old_versions: target version: {target_version}")
        stmt = delete(Project).where(Project.info_version < target_version)
        session.execute(stmt)

    def delete_by_dir_and_lib_(self, session: Session, dir_name: str, lib: Lib):
        log.debug(f"delete_by_dir_and_lib: {dir_name}, {lib.name}", )
        stmt = select(Project).filter_by(dir_name=dir_name, lib=lib.name)

        project = session.scalars(self.all_projects.filter_by(dir_name=dir_name, lib=lib.name)).first()

        if project:
            session.delete(project)
            session.commit()

            log.debug("project deleted from db")
        else:
            log.error("Project not found in db")

    def get_dirs_(self, session: Session, lib_name: str = None):
        log.debug("get_dirs")
        log.debug(lib_name)

        if lib_name is not None:
            selected_lib = select(Project).filter_by(lib=lib_name)
        else:
            selected_lib = select(Project)

        selected_lib = session.scalars(selected_lib).all()
        dirs = set([value.dir_name for value in selected_lib])
        log.debug(dirs)
        log.debug(f"get_dirs: {len(dirs)}")

        return dirs

    def delete_all_data_(self, session: Session) -> None:
        log.info("delete_all_data")

        # noinspection PyTypeChecker
        session.exec(delete(Project))
        # noinspection PyTypeChecker
        session.exec(delete(PoolVariant))

    def backup_variants(self):
        log.debug("backup_variants")
        with dep.Session() as session, FileSession() as fs:
            in_db = session.scalar(
                select(PoolVariant).order_by(desc(PoolVariant.update_time))
            )

            if in_db:
                version_in_db = in_db.update_time
            else:
                version_in_db = datetime(2000, 1, 1)

            variants_file = Variants.load()

            if variants_file.date > version_in_db:
                log.debug(f"backup_variants: in db are outdated: {version_in_db}")
                log.debug(f"backup_variants: updating variants in db from file: {variants_file.date}")
                variants_file.date = version_in_db
                # noinspection PyTypeChecker
                session.exec(delete(PoolVariant))
                variants = variants_file.variants
                session.add_all(variants)
                session.commit()
            else:
                log.debug(f"backup_variants: in db are relevant: {version_in_db}")
                if variants_file.date == version_in_db:
                    log.debug(f"backup_variants: in file are relevant: {variants_file.date}")
                    return

                if variants_file.date < version_in_db:
                    log.debug(f"backup_variants: in file are outdated: {variants_file.date}")
                    log.debug("backup_variants: updating variants in file from db")
                    variants_in_db = session.scalars(
                        select(PoolVariant).order_by(desc(PoolVariant.update_time))
                    ).all()

                    variants_file.variants = variants_in_db
                    variants_file.date = variants_in_db[0].update_time
                    variants_file.save()
                    log.debug(f"backup_variants: variants file saved. "
                              f"Date: {variants_file.date}. "
                              f"Count: {len(variants_file.variants)}.")

    # def update_aliases_(self, session: Session, fs: FSession):
    #     aliases = utils.get_aliases()
    #     aliases["nothing"] = "nothing"
    #     stmt = [
    #         or_(
    #             Project.tag.icontains(f'"{alias}"'),
    #             Project.artist.icontains(f'"{alias}"'),
    #             Project.character.icontains(f'"{alias}"'),
    #             Project.parody.icontains(f'"{alias}"'),
    #             Project.group.icontains(f'"{alias}"'),
    #         )
    #         for alias in aliases.keys()
    #     ]
    #
    #     incorrect_aliases = session.scalars(self.active_projects.where(or_(*stmt))).all()
    #
    #     for project in incorrect_aliases:
    #         projecte = Project.project_load_from_db(session, fs, project.lid)
    #         update = defaultdict(list)
    #
    #         for category in ["tag", "artist", "group", "parody", "character", "language"]:
    #             items = getattr(projecte, category)
    #             new_items = []
    #             for item in items:
    #                 if not item:
    #                     continue
    #                 if item not in aliases:
    #                     new_items.append(item)
    #                 else:
    #                     if isinstance(aliases[item], str):
    #                         # noinspection PyUnresolvedReferences
    #                         new_items.append(aliases[item])
    #                     elif isinstance(aliases[item], list):
    #                         new_items.extend(aliases[item])
    #                     else:
    #                         raise Exception(f"Unknown item {item}")
    #
    #             update[category] = list(set(new_items))
    #
    #         update = dict(update)
    #         # noinspection PyDictCreation
    #         projecte_updated = projecte.model_copy(update=update)
    #         projecte_updated.renew_search_body()
    #
    #         projecte_updated.update_(session, fs=fs)

    def delete_pool_(self, session: Session, pool_lid: str) -> None:
        log.debug(f"delete_pool_: {pool_lid}")

        projects_in_pool_lids = session.scalars(select(PoolVariant.project).where(
            PoolVariant.lid == pool_lid
        )).all()
        log.debug(f"delete_pool_: found projects: {projects_in_pool_lids}")

        # noinspection PyTypeChecker
        session.execute(
            delete(PoolVariant).where(
                PoolVariant.lid == pool_lid
            )
        )

        # noinspection PyTypeChecker
        session.execute(
            delete(Project).where(
                Project.lid == pool_lid
            )
        )

        log.debug(f"delete_pool_: pool deleted: {pool_lid}")

        session.execute(
            update(Project).where(
                Project.lid.in_(projects_in_pool_lids)
            ).values(active=True)
        )
        log.debug(f"delete_pool_: projects activated: {projects_in_pool_lids}")

    def check_lids_(self, session: Session, lids: list) -> int:
        log.debug(f"check_lids: {lids}")
        stmt = select(func.count(Project.lid)).where(Project.lid.in_(lids))

        return session.scalar(stmt)

    def update_pools_(self, session: Session):
        log.debug("update_pools_")

        pools_entries = session.scalars(
            select(PoolVariant).where(
                PoolVariant.priority == 1
            )
        ).all()

        pools = []

        for pool_entry in pools_entries:
            log.debug(f"update_pools_: {pool_entry}")
            lid = pool_entry.lid

            if session.scalar(select(Project).where(Project.lid == lid)):
                log.debug(f"update_pools_: pool found: {pool_entry}: continue")
                continue

            priority = session.scalar(
                select(Project).where(
                    Project.lid == pool_entry.project,
                )
            )

            pool = Project(
                lid=lid,
                active=True,
                **priority.model_dump(exclude={"lid", "id", "active"})
            )

            pool.pool_sync_(session)

            pools.append(pool)
            log.debug(f"update_pools_: new pool created: {pool.lid}")

        session.add_all(pools)

        projects_with_pool = session.scalars(
            select(PoolVariant.project)
        ).all()

        session.execute(
            update(Project).where(
                Project.lid.in_(projects_with_pool)
            ).values(active=0)
        )
