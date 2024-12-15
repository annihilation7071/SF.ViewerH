import os
from backend.db.connect import Project, get_session
from sqlalchemy import desc, and_, func
from datetime import datetime
from collections import defaultdict
from backend import utils
from backend import logger
from backend.editor import variants_editor
from sqlalchemy.dialects.sqlite import JSON


# noinspection PyMethodMayBeStatic,PyProtectedMember
class Projects:
    def __init__(self, ppg: int = 60):
        self.session = get_session()
        self.libs = utils.read_libs()
        active_libs = [lib for lib, val in self.libs.items() if val["active"] is True]
        self.all_projects = self.session.query(Project).filter(Project.lib.in_(active_libs))
        self.active_projects = self.all_projects.filter(Project.active == 1)
        self.projects = self.active_projects.order_by(desc(Project.upload_date))
        self.search = ""
        self.ppg = ppg

    def _get_project_path(self, project: Project) -> str:
        lib = project.lib
        lib_dir = self.libs[lib]["path"]
        project_dir = project.dir_name
        project_path = os.path.abspath(os.path.join(lib_dir, project_dir))
        return project_path

    def _get_project_preview_path(self, project: Project) -> str:
        project_path = self._get_project_path(project)
        preview_name = project.preview
        preview_path = os.path.abspath(os.path.join(project_path, preview_name))
        return preview_path

    def _normalize_search(self, search: str) -> str:
        search = search.split(",")
        search = [item.strip().lower().replace("\r", "").replace("\n", "").replace("_", " ").strip() for item in search]
        search = ",".join(search)
        return search

    def _get_flags_paths(self, languages: list) -> list:
        print(languages)
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

        print(flags)
        return flags

    def db(self):
        return self.session

    def len(self):
        return self.projects.count()

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
        print(search)
        self.projects = self.active_projects.filter(and_(*search_query))
        self.projects = self.projects.order_by(desc(Project.upload_date))
        print(f"search: {search}")

    def get_page(self, page: int = 1, search: str = None):
        self._filter(search)

        selected_projects = self.projects.offset(((page - 1) * self.ppg)).limit(self.ppg)
        projects = []
        for project in selected_projects:
            projects.append({
                "id": project._id,
                "lid": project.lid,
                "title": project.title,
                "subtitle": project.subtitle,
                "preview_path": self._get_project_preview_path(project),
                "flags": self._get_flags_paths(project.language),
                "lvariants_count": len(project.lvariants),
            })
        print(projects)
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

        dict_project = project.to_dict()
        dict_project["variants_view"] = [variant.split(":")[1] for variant in dict_project["lvariants"]]
        # dict_project["variants_view"] = [variant for variant in dict_project["variants_view"] if len(variant) > 0]
        dict_project["path"] = self._get_project_path(project)
        dict_project["id"] = dict_project["_id"]
        dict_project["preview_path"] = self._get_project_preview_path(project)
        dict_project["upload_date_str"] = dict_project["upload_date"].strftime("%Y-%m-%dT%H:%M:%S")

        print(dict_project)
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
            print(f"Row deleted: {lib_name}: {dir_name}")
        else:
            print(f"Row not found: {lib_name}: {dir_name}")

    def count_item(self, item: str) -> list:
        result = defaultdict(int)

        items_strings = self.active_projects.with_entities(getattr(Project, item)).all()

        for items_string in items_strings:
            items = items_string[0].split(";;;")
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

    def update_pools_v(self, force: bool = False):
        variants = self.session.query(Project.lvariants).filter(
            func.json_array_length(Project.lvariants) > 0).distinct().all()

        variants = [variant[0] for variant in variants]
        for variant in variants:
            exist_pool = self.session.query(Project).filter(Project.lvariants == variant,
                                                            Project.lid.icontains("pool_"))
            if (count := exist_pool.count()) > 0:
                if force is True or count > 1:
                    exist_pool.delete()
                    self.session.commit()
                else:
                    return

            variants_editor.edit(self, variant)

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
        print(project)
        _id = project["_id"]
        columns = self.get_columns(exclude=["_id"])

        project = {column: project[column] for column in columns}
        project["search_body"] = make_search_body(project)

        self.session.query(Project).filter_by(_id=_id).update(project)
        self.session.commit()


def make_search_body(project: dict):
    include = ["source_id", "source", "url", "downloader", "title", "subtitle",
               "parody", "character", "tag", "artist", "group", "language",
               "category", "series"]

    search_body = ";;;"

    for k, v in project.items():
        if k in include:
            for item in v:
                search_body += f"{k}:{item.lower()};;;"

    return search_body


def prepare_to_db(project: dict) -> dict:
    def f(x):
        try:
            d = datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')
            print(d)
            return d
        except:
            print(x)
            pass
        return x

    project = {k: f(v) for k, v in project.items()}

    project["search_body"] = make_search_body(project)

    return project
