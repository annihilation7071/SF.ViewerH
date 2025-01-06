import os

from backend.db.connect import Project, get_session
from sqlalchemy import desc, and_, func, or_
from collections import defaultdict
from backend.editor import variants_editor
from backend import logger, utils
from backend.logger import log
from backend.editor import eutils
from icecream import ic
ic.configureOutput(includeContext=True)


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self):
        self.Session = get_session()
        self.session = self.Session()
        self.libs = utils.read_libs(only_active=True, check=True)
        # active_libs = [lib for lib, val in self.libs.items() if val["active"] is True]
        self.all_projects = self.session.query(Project).filter(Project.lib.in_(self.libs))
        self.active_projects = self.all_projects.filter(Project.active == 1)
        self.sorting_method = Project.upload_date
        self.projects = self.active_projects.order_by(desc(self.sorting_method))
        self.search = ""

    def _get_project_path(self, project: Project) -> str:
        lib = project.lib
        lib_dir = self.libs[lib].path
        project_dir = project.dir_name
        project_path = os.path.abspath(os.path.join(lib_dir, project_dir))
        return project_path

    def _normalize_search(self, search: str) -> str:
        search = search.split(",")
        search = [item.strip().lower().replace("\r", "").replace("\n", "").replace("_", " ").strip() for item in search]
        search = ",".join(search)
        return search

    def _get_flags_paths(self, languages: list) -> list:
        exclude = ["rewrite", "translated"]
        # exclude = []
        flags_path = os.path.join(os.getcwd(), f"data/flags")
        supports = os.listdir(flags_path)
        supports = [os.path.splitext(flag)[0] for flag in supports]
        flags = []
        for language in languages:
            language = language.lower()
            if language in supports:
                path = os.path.join(os.getcwd(), f"data/flags/{language}.svg")
                flags.append(path)
            else:
                if language not in exclude:
                    logger.log(f"Flags not found: {language}", file="log-flags.txt")
                    path = os.path.join(os.getcwd(), f"data/flags/unknown.png")
                    flags.append(path)

        return flags

    def _get_project_preview_path(self, project: Project) -> str:
        project_path = self._get_project_path(project)
        preview_name = ""

        for file in os.listdir(project_path):
            if file.startswith("preview") or file.startswith("_preview"):
                preview_name = file
                break

        if preview_name == "":
            preview_name = project.preview

        preview_path = os.path.abspath(os.path.join(project_path, preview_name))
        return preview_path

    def _gen_extra_parameters(self, project: Project) -> dict:
        project_path = self._get_project_path(project)
        files = os.listdir(project_path)

        # Preview
        preview_name = ""

        for file in files:
            if file.startswith("preview") or file.startswith("_preview"):
                preview_name = file
                break

        if preview_name == "" or preview_name == project.preview:
            preview_name = project.preview
        else:
            preview_path = os.path.abspath(os.path.join(project_path, preview_name))
            preview_hash = utils.get_imagehash(preview_path)

            utils.update_vinfo(project_path, ["preview", "preview_hash"], [preview_name, preview_hash])

            project.preview = preview_name
            project.preview_hash = preview_hash
            self.session.commit()

        preview_path = os.path.abspath(os.path.join(project_path, preview_name))

        # Pages
        exts = {".png", ".jpg", ".jpeg", ".gif", ".avif", ".webp",
                ".bmp", ".tif", ".tiff", ".apng",
                ".mng", ".flif", ".bpg", ".jxl", ".qoi", ".hif"}
        pages = len([file for file in files if os.path.splitext(file)[1] in exts])

        return {
            "path": self._get_project_path(project),
            "preview_path": preview_path,
            "pages": pages,
            "upload_date_str": project.upload_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "variants_view": [variant.split(":")[1] for variant in project.lvariants],
            "flags": self._get_flags_paths(project.language),
            "lvariants_count": len(project.lvariants),
        }

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
        ic(str(self.projects))

        selected_projects = self.projects.offset(((page - 1) * ppg)).limit(ppg)
        projects = []
        for project in selected_projects:
            projects.append({**project.to_dict(), **self._gen_extra_parameters(project)})

        return projects

    def db(self):
        return self.session

    def len(self):
        return self.projects.count()

    def checking(self):
        self.update_pools_v()
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
            dict_project = {**project.to_dict(), **self._gen_extra_parameters(project)}
            update = defaultdict(list)

            for category in ["tag", "artist", "group", "parody", "character", "language"]:
                items = dict_project[category]
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
            dict_project = {**dict_project, **update}
            update["search_body"] = make_search_body(dict_project)
            dict_project["search_body"] = update["search_body"]

            if project.lid.startswith("pool_") is False:
                eutils.update_data(self, dict_project, list(update.keys()), list(update.values()), multiple=True)
            else:
                self.session.query(Project).filter_by(_id=project._id).update(update)
                self.session.commit()

    def get_project(self, _id: int | str = None, lid: str = None) -> dict | None:
        ic(_id, lid)
        if _id is None and lid is None:
            raise ValueError("Either id or lig must be provided")

        if _id is not None and lid is not None:
            raise ValueError("Only one of id or lig must be provided")

        if isinstance(_id, str):
            _id = int(_id)

        if _id is not None:
            project = self.session.query(Project).filter_by(_id=_id).first()
            ic(project.title)
        else:
            project = self.session.query(Project).filter_by(lid=lid).first()
            ic(project.title)

        if project is None:
            return None

        dict_project = {**project.to_dict(), **self._gen_extra_parameters(project)}

        return dict_project

    def get_project_by_id(self, _id: int | str) -> dict | None:
        return self.get_project(_id=_id)

    def get_project_by_lid(self, lid: str) -> dict | None:
        return self.get_project(lid=lid)

    def get_dirs(self, lib_name: str = None):
        if lib_name is not None:
            selected_lib = self.all_projects.filter_by(lib=lib_name)
        else:
            selected_lib = self.all_projects

        selected_lib = selected_lib.with_entities(Project.dir_name).all()
        dirs = set([dir_name[0] for dir_name in selected_lib])
        logger.log(f"Selected dirs count: {len(dirs)}")

        return dirs

    def get_columns(self, exclude: list | tuple = None):
        # noinspection PyTypeChecker
        columns = [column.name for column in Project.__table__.columns]
        if exclude is not None:
            columns = list(set(columns) - set(exclude))
        return columns

    def delete_by_dir_and_lib(self, dir_name: str, lib_name: str):
        selected_lib = self.all_projects.filter_by(dir_name=dir_name, lib=lib_name).first()

        if selected_lib:
            self.session.delete(selected_lib)
            self.session.commit()
            log(f"Row deleted: {lib_name}: {dir_name}", "../db")
        else:
            log(f"Trying to delete; Row not found: {lib_name}: {dir_name}", "../db")

    def delete_pool(self, variants: list) -> None:
        self.session.query(Project).filter(and_(Project.lid.icontains("pool_"), Project.lvariants == variants)).delete()
        self.session.commit()

    def delete_all_data(self):
        self.session.query(Project).delete()
        self.session.commit()

    def count_item(self, item: str) -> list:
        result = defaultdict(int)

        items_strings = self.active_projects.with_entities(getattr(Project, item)).all()

        for items in items_strings:
            items = items[0]
            for item in items:
                result[item] += 1

        return sorted(result.items(), key=lambda x: x[1], reverse=True)

    def clear_old_versions(self, target_version: int):
        self.session.query(Project).filter(Project.info_version < target_version).delete()
        self.session.commit()

    def check_lids(self, lids: list) -> int:
        return self.all_projects.filter(Project.lid.in_(lids)).count()

    # noinspection da
    def create_priority(self, priority: list, non_priority: list, lid: str = None, update: bool = False) -> None:
        ic()
        if update is True and lid is None:
            raise ValueError("For update priority lid must be provided")
        elif update is False and lid is not None:
            raise ValueError("Lid should be provided only if update is True")

        # priority and non_priority:
        # [[lid, description], [lid, despription]]
        pool = self.get_project_by_lid(priority[0][0])
        pool["lid"] = f"pool_{utils.gen_lid()}" if lid is None else lid
        pool.pop("_id", None)
        pool["active"] = True
        ic(pool["lid"])

        # union some data
        for _lid in non_priority:
            nproject = self.get_project_by_lid(_lid[0])
            pool["tag"] = list(set(pool["tag"]) | set(nproject["tag"]))
            pool["language"] = list(set(pool["language"]) | set(nproject["language"]))
            pool["group"] = list(set(pool["group"]) | set(nproject["group"]))
            pool["artist"] = list(set(pool["artist"]) | set(nproject["artist"]))
            pool["series"] = list(set(pool["series"]) | set(nproject["series"]))
            pool["parody"] = list(set(pool["parody"]) | set(nproject["parody"]))

        pool["search_body"] = make_search_body(pool)

        # add pool to DB
        if lid is None:
            ic("Add new pool")
            self.add_project(pool)
            self.session.commit()
        else:
            ic("Update existing pool")
            self.update_item(pool, key="lid")

        # deactivate original projects
        lids = [p[0] for p in (priority + non_priority)]
        self.all_projects.filter(Project.lid.in_(lids)).update({Project.active: False})

        self.session.commit()
        return pool["lid"]

    def update_priority(self, project: dict):
        ic()
        pool = self.session.query(Project).filter(
            Project.lvariants == project["lvariants"],
            Project.lid.startswith("pool_")
        ).all()

        if len(pool) == 0:
            raise ValueError("No pool found")
        elif len(pool) > 2:
            raise ValueError("Too many pool found")

        pool = pool[0]

        priority, non_priority = variants_editor.separate_priority(pool.lvariants)

        self.create_priority(priority, non_priority, lid=pool.lid, update=True)

    def update_pools_v(self, force: bool = False):
        projects_with_variants = self.session.query(Project).filter(
            func.json_array_length(Project.lvariants) > 0).all()

        unique_variants = []
        unique_check = set()
        for project in projects_with_variants:
            if str(project.lvariants) not in unique_check:
                unique_check.add(str(project.lvariants))
                unique_variants.append(project)

        projects_with_variants = unique_variants
        ic(projects_with_variants)

        for project in projects_with_variants:
            ic(project.lid, project.title)
            variant = project.lvariants
            exist_pool = self.session.query(Project).filter(Project.lvariants == variant,
                                                            Project.lid.istartswith("pool")).all()

            if len(exist_pool) > 0:
                ic("Pool is found")
                if force is True or len(exist_pool) > 1:
                    ic("More than one pool found")
                    exist_pool.delete()
                    self.session.commit()
                else:
                    self.session.query(Project).filter(Project.lvariants == variant).update({Project.active: False})
                    exist_pool[0].active = True
                    self.session.commit()
                    continue

            ic("create new pool")
            dict_project = {**project.to_dict(), **self._gen_extra_parameters(project)}

            variants_editor.edit(self, dict_project, variant)

    def update_item(self, project: dict, key: str = "_id"):
        ic()
        if key == "_id":
            _id = project["_id"]
        elif key == "lid":
            lid = project["lid"]

        columns = self.get_columns(exclude=["_id"])

        project["search_body"] = make_search_body(project)
        project = {column: project[column] for column in columns}
        ic(project)

        if key == "_id":
            ic()
            # noinspection PyUnboundLocalVariable
            self.session.query(Project).filter_by(_id=_id).update(project)
        elif key == "lid":
            ic()
            # noinspection PyUnboundLocalVariable
            self.session.query(Project).filter_by(lid=lid).update(project)
        self.session.commit()

    def add_project(self, project: dict):
        columns = self.get_columns(exclude=["_id", "active", "search_body"])

        project = {column: project[column] for column in columns}
        project["search_body"] = make_search_body(project)
        project = Project(**project)
        ic(f"Project added to DB: {project.title}")

        self.session.add(project)
        self.session.commit()


def make_search_body(project: dict):
    include = ["source_id", "source", "url", "downloader", "title", "subtitle",
               "parody", "character", "tag", "artist", "group", "language",
               "category", "series", "lib"]

    search_body = ";;;"

    for k, v in project.items():
        if k in include:
            if isinstance(v, list):
                for item in v:
                    search_body += f"{k}:{item.lower()};;;"
            else:
                search_body += f"{k}:{v};;;"

    return search_body
