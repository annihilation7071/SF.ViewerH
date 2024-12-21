import os
import json
from backend.db.connect import Project, get_session
from sqlalchemy import desc, and_, func, or_
from datetime import datetime
from collections import defaultdict
from backend.editor import variants_editor
from sqlalchemy.dialects.sqlite import JSON
from backend import cmdargs, logger, utils
from importlib import import_module
from backend.logger import log
from backend.editor import eutils


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self):
        self.session = get_session()
        self.libs = utils.read_libs()
        active_libs = [lib for lib, val in self.libs.items() if val["active"] is True]
        self.all_projects = self.session.query(Project).filter(Project.lib.in_(active_libs))
        self.active_projects = self.all_projects.filter(Project.active == 1)
        self.projects = self.active_projects.order_by(desc(Project.upload_date))
        self.search = ""

    def _get_project_path(self, project: Project) -> str:
        lib = project.lib
        lib_dir = self.libs[lib]["path"]
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

        if preview_name == "":
            preview_name = project.preview

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
            "id": project._id,
            "upload_date_str": project.upload_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "variants_view": [variant.split(":")[1] for variant in project.lvariants],
            "flags": self._get_flags_paths(project.language),
            "lvariants_count": len(project.lvariants),
        }

    def db(self):
        return self.session

    def len(self):
        return self.projects.count()

    def update_projects(self):
        update_projects(self)
        self.update_pools_v()

    def _filter(self, search: str | None):
        search = self._normalize_search(search)

        if self.search == search:
            return

        if search is None or search == "":
            self.search = ""
            self.projects = self.active_projects.order_by(desc(Project.upload_date))
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
        self.projects = self.projects.order_by(desc(Project.upload_date))

    def get_page(self, ppg: int, page: int = 1, search: str = None):
        self._filter(search)

        selected_projects = self.projects.offset(((page - 1) * ppg)).limit(ppg)
        projects = []
        for project in selected_projects:
            projects.append({**project.to_dict(), **self._gen_extra_parameters(project)})

        return projects

    def get_project(self, _id: int | str = None, lid: str = None) -> dict:
        if _id is None and lid is None:
            raise ValueError("Either id or lig must be provided")

        if _id is not None and lid is not None:
            raise ValueError("Only one of id or lig must be provided")

        if isinstance(_id, str):
            _id = int(_id)

        if _id is not None:
            project = self.session.query(Project).filter_by(_id=_id).first()
        else:
            project = self.session.query(Project).filter_by(lid=lid).first()

        dict_project = {**project.to_dict(), **self._gen_extra_parameters(project)}

        return dict_project

    def get_project_by_id(self, _id: int | str) -> dict:
        return self.get_project(_id=_id)

    def get_project_by_lid(self, lid: str) -> dict:
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

    def delete_by_dir_and_lib(self, dir_name: str, lib_name: str):
        selected_lib = self.all_projects.filter_by(dir_name=dir_name, lib=lib_name).first()

        if selected_lib:
            self.session.delete(selected_lib)
            self.session.commit()
            log(f"Row deleted: {lib_name}: {dir_name}", "DB")
        else:
            log(f"Trying to delete; Row not found: {lib_name}: {dir_name}", "DB")

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

    def delete_all_data(self):
        self.session.query(Project).delete()
        self.session.commit()

    def check_lids(self, lids: list) -> int:
        return self.all_projects.filter(Project.lid.in_(lids)).count()

    def delete_pool(self, variants: list) -> None:
        self.session.query(Project).filter(and_(Project.lid.icontains("pool_"), Project.lvariants == variants)).delete()
        self.session.commit()

    def create_priority(self, priority: list, non_priority: list):
        # priority and non_priority:
        # [[lid, description], [lid, despription]]
        pool = self.get_project_by_lid(priority[0][0])
        pool["lid"] = f"pool_{utils.gen_lid()}"
        pool.pop("_id", None)

        # union some data
        for lid in non_priority:
            nproject = self.get_project_by_lid(lid[0])
            pool["tag"] = list(set(pool["tag"]) | set(nproject["tag"]))
            pool["language"] = list(set(pool["language"]) | set(nproject["language"]))
            pool["group"] = list(set(pool["group"]) | set(nproject["group"]))
            pool["artist"] = list(set(pool["artist"]) | set(nproject["artist"]))
            pool["series"] = list(set(pool["series"]) | set(nproject["series"]))
            pool["parody"] = list(set(pool["parody"]) | set(nproject["parody"]))

        # add pool to DB
        self.add_project(pool)

        # deactivate original projects
        lids = [p[0] for p in (priority + non_priority)]
        self.all_projects.filter(Project.lid.in_(lids)).update({Project.active: False})

        self.session.commit()
        return pool["lid"]

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

        log(f"Selected projects with variants: {len(projects_with_variants)}", "variants-3")
        for project in projects_with_variants:
            log(f"Selected projects: {project.lid}: {project.title}: {project.lvariants}", "variants-3")

        for project in projects_with_variants:
            log(f"Project: {project.lid}: start", "variants-3")
            variant = project.lvariants
            exist_pool = self.session.query(Project).filter(Project.lvariants == variant,
                                                            Project.lid.icontains("pool_"))
            log(f"Exist pools: {[pool.lid for pool in exist_pool]}", "variants-3")
            if (count := exist_pool.count()) > 0:
                if force is True or count > 1:
                    exist_pool.delete()
                    self.session.commit()
                else:
                    continue

            dict_project = {**project.to_dict(), **self._gen_extra_parameters(project)}

            log(f"Project: {project.lid}: send to variant-editor", "variants-3")
            variants_editor.edit(self, variant, dict_project)
            log(f"Project: {project.lid}: received from variant-editor", "variants-3")

    def update_aliases(self):
        aliases = utils.get_aliases()
        search_query = [
            or_(
                func.json_each_text(Project.tag) == alias,
                func.json_each_text(Project.artist) == alias,
                func.json_each_text(Project.character) == alias,
                func.json_each_text(Project.group) == alias,
                func.json_each_text(Project.parody) == alias
            )
            for alias in aliases.keys()
        ]
        incorrect_aliases = self.active_projects.filter(or_(*search_query)).all()

        for project in incorrect_aliases:
            dict_project = project.to_dict()
            update = defaultdict(list)

            for category in ["tag", "artist", "group", "parody", "character"]:
                items = dict_project[category]
                items = [item if (item not in aliases) else item for item in items if item]
                update[category] = items

            update = dict(update)
            # noinspection PyDictCreation
            dict_project = {**dict_project, **update}
            update["search_body"] = make_search_body(dict_project)
            dict_project["search_body"] = update["search_body"]

            if project.lid.startswith("pool_") is False:
                eutils.update_data(self, dict_project, list(update.keys()), update.values(), multiple=True)
            else:

                self.session.query(Project).filter_by(_id=project._id).update(update)
                self.session.commit()

    def get_columns(self, exclude: list | tuple = None):
        # noinspection PyTypeChecker
        columns = [column.name for column in Project.__table__.columns]
        if exclude is not None:
            columns = list(set(columns) - set(exclude))
        return columns

    def add_project(self, project: dict):
        logger.log(project, file="log-3.txt")
        columns = self.get_columns(exclude=["_id", "active", "search_body"])

        project = {column: project[column] for column in columns}
        project["search_body"] = make_search_body(project)
        project = Project(**project)

        self.session.add(project)
        self.session.commit()

    def update_item(self, project: dict):
        _id = project["_id"]
        columns = self.get_columns(exclude=["_id"])

        project = {column: project[column] for column in columns}
        project["search_body"] = make_search_body(project)

        self.session.query(Project).filter_by(_id=_id).update(project)
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


def update_projects(projects: Projects) -> None:
    libs = utils.read_libs()

    for lib_name, lib_data in libs.items():
        if lib_data["active"] is False:
            continue

        logger.log(f"Processing: {lib_name}")
        if cmdargs.args.reindex is True:
            cmdargs.args.reindex = False
            projects.delete_all_data()
            logger.log(f"Deleted all data")

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info = json.load(f)

        projects.clear_old_versions(v_info["info_version"])

        processor = import_module(f"backend.processors.{lib_data['processor']}")

        path = lib_data["path"]
        dirs = get_dirs(path, processor.meta_file)

        dirs_not_in_db, dirs_not_exist = check_dirs(projects, lib_name, dirs)

        for dir in dirs_not_exist:
            log(f"Dir not exist: {dir}", "check-dirs")
            projects.delete_by_dir_and_lib(dir, lib_name)

        for dir in dirs_not_in_db:
            project_path = str(os.path.join(path, dir))

            if cmdargs.args.rewrite_v_info is True:
                processor.make_v_info(project_path)

            project = get_v_info(project_path)
            if project is None:
                processor.make_v_info(project_path)
                project = get_v_info(project_path)

            project["lib"] = lib_name
            project["dir_name"] = dir
            project["upload_date"] = datetime.strptime(project["upload_date"], "%Y-%m-%dT%H:%M:%S")
            projects.add_project(project)


def get_dirs(path: str, meta_file: str) -> list[str]:
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def check_dirs(projects: Projects, lib_name: str, dirs: list[str]) -> tuple:
    exist_dirs = set(dirs)
    dirs_in_db = set(projects.get_dirs(lib_name))

    dirs_not_in_db = exist_dirs - dirs_in_db
    logger.log(f"Directories not in DB: {len(dirs_not_in_db)}")
    dirs_not_exist = dirs_in_db - exist_dirs
    logger.log(f"Directories in DB but not exist: {len(dirs_not_exist)}")

    return dirs_not_in_db, dirs_not_exist


def get_v_info(path: str) -> dict | None:
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info = json.load(f)

    if os.path.exists(os.path.join(path, "sf.viewer/v_info.json")):
        with open(os.path.join(path, "sf.viewer/v_info.json"), "r", encoding='utf-8') as f:
            v_info_exist = json.load(f)

        if v_info_exist["info_version"] == v_info["info_version"]:
            return v_info_exist
        else:
            raise IOError("v_info version is not corrected")

    else:
        return None
