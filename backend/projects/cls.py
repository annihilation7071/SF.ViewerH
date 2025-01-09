from backend import dep
from backend.classes.db import Project
from sqlalchemy import desc, and_, func, or_
from collections import defaultdict
from backend.editor import variants_editor
from backend import utils
from icecream import ic
from backend.classes.projecte import ProjectE, ProjectEPool
from backend.classes.templates import ProjectTemplateDB
from backend.logger_new import get_logger
from sqlalchemy.orm import Session
from sqlalchemy import select

ic.configureOutput(includeContext=True)

log = get_logger("Projects")


class ProjectsError(Exception):
    pass


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self):
        log.debug("load projects...")
        self.libs = utils.read_libs(only_active=True, check=True)
        # active_libs = [lib for lib, val in self.libs.items() if val["active"] is True]
        # self.all_projects = self.session.query(Project).filter(Project.lib.in_(self.libs))
        self.all_projects = select(Project).filter(Project.lib.in_(dep.libs))
        # self.active_projects = self.all_projects.filter(Project.active == 1)
        self.active_projects = self.all_projects.filter(Project.active == 1)
        self.sorting_method = Project.upload_date
        # self.projects = self.active_projects.order_by(desc(self.sorting_method))
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
            ic(f"Sorting method {method} selected")
        else:
            raise Exception(f"Method {method} not supported")

    def get_page(self, ppg: int, page: int = 1, search: str = None):
        self._filter(search)

        projects = []

        with dep.Session() as session:
            selected_projects = session.scalars(self.projects.offset(((page - 1) * ppg)).limit(ppg))

            for project in selected_projects:
                projects.append(ProjectE.load_from_db(project.lid, session))

            session.commit()

        return projects

    def len(self):
        with dep.Session() as session:
            return len(session.scalars(self.projects).all())

    def checking(self):
        self.update_pools()
        self.update_aliases()

    def update_aliases(self):
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

        with dep.Session() as session:

            incorrect_aliases = session.scalars(self.active_projects.filter(or_(*search_query))).all()

            for project in incorrect_aliases:
                projecte = ProjectE(lib_data=self.libs[project.lib], **project.to_dict())
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

                projecte_updated.soft_update(session)

            session.commit()

    def get_project(self, lid: str) -> ProjectE:
        log.debug("get_project")
        with dep.Session() as session:
            return ProjectE.load_from_db(lid, session)

    def get_project_by_lid(self, lid: str) -> ProjectE:
        return self.get_project(lid=lid)

    def get_dirs(self, lib_name: str = None):
        log.debug("get_dirs")
        log.debug(lib_name)
        with dep.Session() as session:
            if lib_name is not None:
                selected_lib = select(Project).filter_by(lib=lib_name)
            else:
                selected_lib = select(Project)

            selected_lib = session.scalars(select(Project)).all()
            dirs = set([value.dir_name for value in selected_lib])
            log.debug(f"get_dirs: {len(dirs)}")

        return dirs

    def _get_columns(self, exclude: list | tuple = None):
        # noinspection PyTypeChecker
        columns = [column.name for column in Project.__table__.columns]
        if exclude is not None:
            columns = list(set(columns) - set(exclude))
        return columns

    def delete_by_dir_and_lib(self, dir_name: str, lib_name: str):
        log.debug(f"delete_by_dir_and_lib: {dir_name}, {lib_name}", )
        stmt = select(Project).filter_by(dir_name=dir_name, lib=lib_name)
        with dep.Session() as session:
            project = session.scalars(self.all_projects.filter_by(dir_name=dir_name, lib=lib_name)).first()

            if project:
                session.delete(project)
                session.commit()

                log.debug("project deleted")
            else:
                log.error("Project not found")

    def delete_pool(self, variants: list) -> None:
        log.debug(f"delete_pool: {variants}")
        with dep.Session() as session:
            session.query(Project).filter(and_(Project.lid.icontains("pool_"), Project.lvariants == variants)).delete()
            session.commit()

    def delete_all_data(self):
        log.info("delete_all_data")
        with dep.Session() as session:
            session.query(Project).delete()
            session.commit()

    def count_item(self, item: str) -> list:
        log.debug(f"count_item: {item}")
        result = defaultdict(int)

        items_strings = self.active_projects.with_entities(getattr(Project, item)).all()

        for items in items_strings:
            items = items[0]
            for item in items:
                result[item] += 1

        return sorted(result.items(), key=lambda x: x[1], reverse=True)

    def clear_old_versions(self, target_version: int):
        log.debug(f"clear_old_versions: target version: {target_version}")
        with dep.Session() as session:
            session.query(Project).filter(Project.info_version < target_version).delete()
            session.commit()

    def check_lids(self, lids: list) -> int:
        log.debug(f"check_lids: {lids}")
        return self.all_projects.filter(Project.lid.in_(lids)).count()

    # noinspection da
    def create_priority(self,
                        priority: list,
                        non_priority: list,
                        variants: list,
                        session: Session,
                        ) -> str:
        log.debug("create_priority")
        log.debug("create new pool")
        log.debug("info",
                  extra={
                      "priority": priority,
                      "non_priority": non_priority,
                  })

        # priority and non_priority:
        # [[lid, description], [lid, despription]]
        priority_project: Project = session.query(Project).filter_by(lid=priority[0][0]).first()
        log.debug(f"priority_project: {priority_project.lid}; {priority_project.title}")

        pool: ProjectEPool = ProjectEPool(**self.get_project_by_lid(priority_project.lid).model_dump())
        pool.lid = f"pool_{utils.gen_lid()}"
        pool._id = None
        pool.lvariants = variants

        log.debug(f"Selected priority: {pool.lid}, {pool.title}")
        log.debug(f"Lid for pool: {pool.lid}")
        pool.active = True

        pool.parse_parameters(session)

        log.debug(f"Add new pool: {pool.lid}")
        pool.add_to_db(session)

        return pool.lid

    def update_pools(self, force: bool = False):
        log.info(f"Updating pools...")

        pool_need_create = []

        with dep.Session() as session:
            projects_with_variants: list[Project] = session.query(Project).filter(
                func.json_array_length(Project.lvariants) > 0).all()
            log.debug(f"Found {len(projects_with_variants)} projects with variants")

            unique_variants = []
            unique_check = set()
            for project in projects_with_variants:
                if str(project.lvariants) not in unique_check:
                    unique_check.add(str(project.lvariants))
                    unique_variants.append(project)

            projects_with_variants = unique_variants
            log.debug(f"Found {len(projects_with_variants)} unique variants")

            for project in projects_with_variants:
                log.debug(f"Processing: {project.lid}; {project.title}")
                variant = project.lvariants
                log.debug(f"Variants: {variant}")
                exist_pool = session.query(Project).filter(Project.lvariants == variant,
                                                                Project.lid.istartswith("pool")).all()

                if len(exist_pool) > 0:
                    log.debug(f"Found existing pool")
                    if force is True or len(exist_pool) > 1:

                        if len(exist_pool) > 1:
                            log.warning(f"More than one pool found. Deliting all pools...")
                        else:
                            log.debug(f"Deleting existing pool")

                        for pool in exist_pool:
                            log.debug(f"Pool deleting: {pool.lid}")
                            session.delete(pool)

                        log.debug(f"All pools were deleted")

                    else:
                        # TODO check later if this need at all or not
                        session.query(Project).filter(Project.lvariants == variant).update({Project.active: False})
                        exist_pool[0].active = True
                        continue

                pool_need_create.append(project.to_dict())
            session.commit()

        for dict_project in pool_need_create:
            log.debug(f"Creaging new pool")
            projecte = ProjectE(
                lib_data=self.libs[dict_project["lib"]],
                **dict_project
            )

            variants_editor.edit(self, projecte, variant)

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




