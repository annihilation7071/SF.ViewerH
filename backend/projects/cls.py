from backend import dep
from backend.db.classes import Project
from sqlalchemy import desc, and_, func, or_
from collections import defaultdict
from backend.editor import variants_editor
from backend import utils
from icecream import ic
from backend.classes.projecte import ProjectE
from backend.classes.templates import ProjectTemplateDB
from backend.logger_new import get_logger

ic.configureOutput(includeContext=True)

log = get_logger("Projects")


class ProjectsError(Exception):
    pass


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self):
        log.debug("load projects...")
        self.session = dep.Session()
        self.libs = utils.read_libs(only_active=True, check=True)
        # active_libs = [lib for lib, val in self.libs.items() if val["active"] is True]
        self.all_projects = self.session.query(Project).filter(Project.lib.in_(self.libs))
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
            ic(f"Sorting method {method} selected")
        else:
            raise Exception(f"Method {method} not supported")

    def get_page(self, ppg: int, page: int = 1, search: str = None):
        self._filter(search)

        selected_projects = self.projects.offset(((page - 1) * ppg)).limit(ppg)
        projects = []
        for project in selected_projects:
            projects.append(ProjectE(lib_data=self.libs[project.lib], **project.to_dict()))

        return projects

    def db(self):
        return self.session

    def len(self):
        return self.projects.count()

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
        incorrect_aliases = self.active_projects.filter(or_(*search_query)).all()

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

            projecte_updated.update()

    def get_project(self, _id: int | str = None, lid: str = None) -> ProjectE:
        log.debug("get_project")
        if _id is None and lid is None:
            raise ValueError("Either id or lig must be provided")

        if _id is not None and lid is not None:
            raise ValueError("Only one of id or lig must be provided")

        if isinstance(_id, str):
            _id = int(_id)

        if _id is not None:
            project = self.session.query(Project).filter_by(_id=_id).first()
            log.debug("by id")
        else:
            project = self.session.query(Project).filter_by(lid=lid).first()
            log.debug("by lid")

        if project is None:
            # noinspection PyTypeChecker
            return None

        return ProjectE(
            lib_data=self.libs[project.lib],
            **project.to_dict()
        )

    def get_project_by_id(self, _id: int | str) -> ProjectE:
        return self.get_project(_id=_id)

    def get_project_by_lid(self, lid: str) -> ProjectE:
        return self.get_project(lid=lid)

    def get_dirs(self, lib_name: str = None):
        log.debug("get_dirs")
        if lib_name is not None:
            selected_lib = self.all_projects.filter_by(lib=lib_name)
        else:
            selected_lib = self.all_projects

        selected_lib = selected_lib.with_entities(Project.dir_name).all()
        dirs = set([dir_name[0] for dir_name in selected_lib])
        log.debug(f"get_dirs: {len(dirs)}")

        return dirs

    def _get_columns(self, exclude: list | tuple = None):
        # noinspection PyTypeChecker
        columns = [column.name for column in Project.__table__.columns]
        if exclude is not None:
            columns = list(set(columns) - set(exclude))
        return columns

    def delete_by_dir_and_lib(self, dir_name: str, lib_name: str):
        log.debug(f"delete_by_dir_and_lib: {dir_name}, {lib_name}")
        project = self.all_projects.filter_by(dir_name=dir_name, lib=lib_name).first()

        if project:
            with dep.Session() as session:
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
                        lid: str = None,
                        update: bool = False) -> str:
        log.debug("create_priority")
        log.debug("create new pool" if update else "update existing pool")
        log.debug("info",
                  extra={
                      "priority": priority,
                      "non_priority": non_priority,
                  })
        try:
            if update is True and lid is None:
                raise ValueError("For update priority lid must be provided")
            elif update is False and lid is not None:
                raise ValueError("Lid should be provided only if update is True")
        except ValueError:
            log.exception("Failed to create priority, incorrect parameters",
                          extra={
                              "lid": lid,
                              "update": update,
                          })

        with dep.Session() as session:
            session.begin()
            # priority and non_priority:
            # [[lid, description], [lid, despription]]
            priority_project: Project = session.query(Project).filter_by(lid=priority[0][0]).first()
            log.debug(f"priority_project: {priority_project.lid}; {priority_project.title}")

            if update:
                pool: Project = session.query(Project).filter(Project.lid == lid).first()
            else:
                pool: Project = Project(
                    lid=f"pool_{utils.gen_lid()}",
                    **priority_project.to_dict(exclude=["_id", "lid"])
                )

            log.debug(f"Selected priority: {pool.lid}, {pool.title}")
            log.debug(f"Lid for pool: {pool.lid}")
            pool.active = True

            for key, value in priority_project.to_dict(exclude=["_id", "lid",
                                                                "search_body",
                                                                "active"]).items():
                setattr(pool, key, value)

            # union some data
            for _lid in non_priority:
                nproject = self.get_project_by_lid(_lid[0])
                pool.tag = list(set(pool.tag) | set(nproject.tag))
                pool.language = list(set(pool.language) | set(nproject.language))
                pool.group = list(set(pool.group) | set(nproject.group))
                pool.artist = list(set(pool.artist) | set(nproject.artist))
                pool.series = list(set(pool.series) | set(nproject.series))
                pool.parody = list(set(pool.parody) | set(nproject.parody))

            pool.search_body = utils.make_search_body(pool)

            # add pool to DB
            if lid is None:
                log.debug(f"Add new pool: {pool.lid}")
                session.add(pool)
            else:
                log.debug(f"Update existing pool: {pool.lid}")

            # deactivate original projects
            lids = [p[0] for p in (priority + non_priority)]
            log.debug(f"Deactivating projects: {lids}")
            session.query(Project).filter(Project.lid.in_(lids)).update({Project.active: False})
            session.commit()

            lid = pool.lid

        return lid

    def update_priority(self, project: ProjectE):
        log.debug(f"update_priority: {project.lid}")

        pool = self.session.query(Project).filter(
            Project.lvariants == project["lvariants"],
            Project.lid.startswith("pool_")
        ).all()

        if len(pool) == 0:
            raise ProjectsError("No pool found")
        elif len(pool) > 2:
            raise ProjectsError("Too many pool found")

        log.debug(f"Pool found: {pool.lid}")

        pool = pool[0]

        priority, non_priority = variants_editor.separate_priority(pool.lvariants)
        log.debug(f"priority: {priority}")
        log.debug(f"non_priority: {non_priority}")

        self.create_priority(priority, non_priority, lid=pool.lid, update=True)

    def update_pools(self, force: bool = False):
        log.info(f"Updating pools...")
        projects_with_variants = self.session.query(Project).filter(
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
            exist_pool = self.session.query(Project).filter(Project.lvariants == variant,
                                                            Project.lid.istartswith("pool")).all()

            if len(exist_pool) > 0:
                log.debug(f"Found existing pool")
                if force is True or len(exist_pool) > 1:

                    if len(exist_pool) > 1:
                        log.warning(f"More than one pool found. Deliting all pools...")
                    else:
                        log.debug(f"Deleting existing pool")

                    with dep.Session() as session:
                        for pool in exist_pool:
                            log.debug(f"Pool deleting: {pool.lid}")
                            session.delete(pool)
                        session.commit()

                    log.debug(f"All pools were deleted")
                else:
                    # TODO check later if this need at all or not
                    # self.session.query(Project).filter(Project.lvariants == variant).update({Project.active: False})
                    # exist_pool[0].active = True
                    # self.session.commit()
                    continue

            log.debug(f"Creaging new pool")
            projecte = ProjectE(
                lib_data=self.libs[project.lib],
                **project.to_dict()
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

    def add_project(self, project: ProjectTemplateDB):
        log.debug(f"add_project")

        if isinstance(project, ProjectTemplateDB) is False:
            log.exception(TypeError("Project must be type ProjectTemplateDB"))

        project = Project(**project.model_dump())
        log.debug(project.upload_date)
        log.info(f"Adding new project: {project.title}")

        with dep.Session() as session:
            session.add(project)
            session.commit()



