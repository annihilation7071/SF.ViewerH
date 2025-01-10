from backend import dep
from backend.classes.db import Project
from sqlalchemy import desc, and_, func, or_, Sequence
from collections import defaultdict
from backend.editor import variants_editor
from backend import utils
from icecream import ic
from backend.classes.projecte import ProjectE, ProjectEPool
from backend.classes.templates import ProjectTemplateDB
from backend import logger
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

ic.configureOutput(includeContext=True)

log = logger.get_logger("Projects")


class ProjectsError(Exception):
    pass


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self):
        log.debug("load projects...")
        log.debug(f"Libs: {dep.libs}")
        self.libs = utils.read_libs(only_active=True, check=True)
        self.all_projects = select(Project).filter(Project.lib.in_(dep.libs))
        self.active_projects = self.all_projects.filter(Project.active == 1)
        self.sorting_method = Project.upload_date
        self.projects = self.active_projects.order_by(desc(self.sorting_method))
        self.search = ""
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
            self.projects = self.active_projects.order_by(desc(self.sorting_method))
            return

        def f(item: str):
            if item.find(":") > -1:
                return f";;;{item};;;"
            else:
                return item

        self.search = search
        search = search.split(",")
        search_query = [Project.search_body.icontains(f(item)) for item in search]

        self.projects = self.active_projects.filter(and_(*search_query))
        self.projects = self.projects.order_by(desc(self.sorting_method))

    def select_sorting_method(self, method: str):
        available = {"upload_date", "preview_hash"}
        if method in available:
            self.sorting_method = getattr(Project, method)
            self.projects = self.projects.order_by(None).order_by(desc(self.sorting_method))
            log.info(f"Sorting method {method} selected")
        else:
            raise ProjectsError(f"Method {method} not supported")

    def get_page(self, session: Session, ppg: int, page: int = 1, search: str = None):
        self._filter(search)

        projects = []

        selected_projects = session.scalars(self.projects.offset(((page - 1) * ppg)).limit(ppg))

        for project in selected_projects:
            projects.append(ProjectE.load_from_db(session, project.lid))

        return projects

    def len(self):
        with dep.Session() as session:
            return len(session.scalars(self.projects).all())

    def renew(self, session: Session):
        self.update_pools(session)
        self.update_aliases(session)

    def update_aliases(self, session: Session):
        aliases = utils.get_aliases()
        aliases["nothing"] = "nothing"
        search_query = [
            or_(
                Project.tag.icontains(f'"{alias}"'),
                Project.artist.icontains(f'"{alias}"'),
                Project.character.icontains(f'"{alias}"'),
                Project.parody.icontains(f'"{alias}"'),
                Project.group.icontains(f'"{alias}"'),
            )
            for alias in aliases.keys()
        ]

        incorrect_aliases = session.scalars(self.active_projects.filter(or_(*search_query))).all()

        for project in incorrect_aliases:
            projecte = ProjectE.load_from_db(dep.libs[project.lib], session)
            update = defaultdict(list)

            for category in ["tag", "artist", "group", "parody", "character", "language"]:
                items = getattr(projecte, category)
                new_items = []
                for item in items:
                    if not item:
                        continue
                    if item not in aliases:
                        new_items.append(item)
                    else:
                        if isinstance(aliases[item], str):
                            new_items.append(aliases[item])
                        elif isinstance(aliases[item], list):
                            new_items.extend(aliases[item])
                        else:
                            raise Exception(f"Unknown item {item}")

                update[category] = list(set(new_items))

            update = dict(update)
            # noinspection PyDictCreation
            projecte_updated = projecte.model_copy(update=update)
            update["search_body"] = utils.make_search_body(projecte_updated)
            projecte_updated.search_body = update["search_body"]

            projecte_updated.update(session)

    def get_project(self, session: Session, lid: str) -> ProjectE:
        log.debug("get_project")
        return ProjectE.load_from_db(session, lid)

    def get_project_by_lid(self, session: Session, lid: str) -> ProjectE:
        return self.get_project(session, lid=lid)

    def get_dirs(self, session: Session, lib_name: str = None):
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

    def _get_columns(self, exclude: list | tuple = None):
        # noinspection PyTypeChecker
        columns = [column.name for column in Project.__table__.columns]
        if exclude is not None:
            columns = list(set(columns) - set(exclude))
        return columns

    def delete_by_dir_and_lib(self, session: Session, dir_name: str, lib_name: str):
        log.debug(f"delete_by_dir_and_lib: {dir_name}, {lib_name}", )
        stmt = select(Project).filter_by(dir_name=dir_name, lib=lib_name)
        with dep.Session() as session:
            project = session.scalars(self.all_projects.filter_by(dir_name=dir_name, lib=lib_name)).first()

            if project:
                session.delete(project)
                session.commit()

                log.debug("project deleted from db")
            else:
                log.error("Project not found in db")

    def delete_pool(self, session: Session, variants: list) -> None:
        log.debug(f"delete_pool: {variants}")
        session.execute(delete(Project).filter(and_(Project.lid.icontains("pool_"), Project.lvariants == variants)))

    def delete_all_data(self, session: Session) -> None:
        log.info("delete_all_data")
        session.query(Project).delete()

    def count_item(self, session: Session, item_: str) -> list:
        log.debug(f"count_item: {item_}")
        result = defaultdict(int)

        projects_ = session.scalars(self.active_projects).all()

        for project in projects_:
            items = getattr(project, item_)
            for item in items:
                result[item] += 1

        return sorted(result.items(), key=lambda x: x[1], reverse=True)

    def clear_old_versions(self, session: Session, target_version: int):
        log.debug(f"clear_old_versions: target version: {target_version}")
        stmt = delete(Project).where(Project.info_version < target_version)
        session.execute(stmt)

    def check_lids(self, session: Session, lids: list) -> int:
        log.debug(f"check_lids: {lids}")
        stmt = select(func.count(Project.lid)).where(Project.lid.in_(lids))

        return session.scalar(stmt)

    # noinspection da
    def create_priority(self,
                        session: Session,
                        variants: list,
                        ) -> str:
        log.debug("create_priority")

        pool = ProjectEPool.create_pool(session, variants)

        return pool.lid

    def update_pools(self, session: Session, force: bool = False):
        log.info(f"Updating pools...")

        pool_need_create = []

        stmt = select(Project).where(func.json_array_length(Project.lvariants) > 0)
        projects_with_variants = session.scalars(stmt).all()

        log.debug(f"projects_with_variants: {len(projects_with_variants)}")

        unique_variants = []
        unique_check = set()
        for project in projects_with_variants:
            if str(project.lvariants) not in unique_check:
                unique_check.add(str(project.lvariants))
                unique_variants.append(project)

        log.debug(f"unique_variants: {len(unique_variants)}")

        for project in unique_variants:
            log.debug(f"Processing: {project.lid}; {project.title}")
            variant = project.lvariants
            log.debug(f"Variants: {variant}")

            pools = (
                Project.lvariants == variant,
                Project.lid.startswith("pool")
            )

            exist_pool = session.scalars(select(Project).where(*pools)).all()

            if len(exist_pool) > 1:
                log.warning(f"More than one pool found. Deliting all pools...")
                session.execute(delete(Project).where(*pools))
                exist_pool = []

            if len(exist_pool) == 1:
                log.debug(f"Found existing pool")
                continue

            if len(exist_pool) == 0:
                log.info(f"Pool not found. Creating new pool...")
                ProjectEPool.create_pool(session, variant)

        #
        # with dep.Session() as session:
        #     projects_with_variants = session.query(Project).filter(
        #         func.json_array_length(Project.lvariants) > 0).all()
        #     log.debug(f"Found {len(projects_with_variants)} projects with variants")
        #
        #     unique_variants = []
        #     unique_check = set()
        #     for project in projects_with_variants:
        #         if str(project.lvariants) not in unique_check:
        #             unique_check.add(str(project.lvariants))
        #             unique_variants.append(project)
        #
        #     projects_with_variants = unique_variants
        #     log.debug(f"Found {len(projects_with_variants)} unique variants")
        #
        #     for project in projects_with_variants:
        #         log.debug(f"Processing: {project.lid}; {project.title}")
        #         variant = project.lvariants
        #         log.debug(f"Variants: {variant}")
        #         exist_pool = session.query(Project).filter(Project.lvariants == variant,
        #                                                         Project.lid.istartswith("pool")).all()
        #
        #         if len(exist_pool) > 0:
        #             log.debug(f"Found existing pool")
        #             if force is True or len(exist_pool) > 1:
        #
        #                 if len(exist_pool) > 1:
        #                     log.warning(f"More than one pool found. Deliting all pools...")
        #                 else:
        #                     log.debug(f"Deleting existing pool")
        #
        #                 for pool in exist_pool:
        #                     log.debug(f"Pool deleting: {pool.lid}")
        #                     session.delete(pool)
        #
        #                 log.debug(f"All pools were deleted")
        #
        #             else:
        #                 # TODO check later if this need at all or not
        #                 session.query(Project).filter(Project.lvariants == variant).update({Project.active: False})
        #                 exist_pool[0].active = True
        #                 continue
        #
        #         pool_need_create.append(project.to_dict())
        #     session.commit()
        #
        # for dict_project in pool_need_create:
        #     log.debug(f"Creaging new pool")
        #     projecte = ProjectE(
        #         lib_data=self.libs[dict_project["lib"]],
        #         **dict_project
        #     )
        #
        #     variants_editor.edit(self, projecte, variant)

    # def update_item(self, project: ProjectE, key: str = "_id"):
    #     log.debug(f"update_item")
    #     if key == "_id":
    #         _id = project["_id"]
    #     elif key == "lid":
    #         lid = project["lid"]
    #
    #     columns = self.get_columns(exclude=["_id"])
    #
    #     project["search_body"] = make_search_body(project)
    #     project = {column: project[column] for column in columns}
    #     ic(project)
    #
    #     if key == "_id":
    #         ic()
    #         # noinspection PyUnboundLocalVariable
    #         self.session.query(Project).filter_by(_id=_id).update(project)
    #     elif key == "lid":
    #         ic()
    #         # noinspection PyUnboundLocalVariable
    #         self.session.query(Project).filter_by(lid=lid).update(project)
    #     self.session.commit()

    # def add_project(self, project: ProjectTemplateDB):
    #     log.debug(f"add_project")
    #
    #     if isinstance(project, ProjectTemplateDB) is False:
    #         log.exception(TypeError("Project must be type ProjectTemplateDB"))
    #
    #     project.add_to_db()
    #
    #     log.info(f"Adding new project: {project.title}")




