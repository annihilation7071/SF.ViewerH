import os
from backend.db.connect import Project, get_session
from sqlalchemy import desc, and_
from datetime import datetime
from collections import defaultdict
from backend import utils
from backend import logger
from backend.editor import variants_editor


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

    def _to_dict(self, project) -> dict:

        def f(item, column_name):
            print(item)
            target_columns = ["lvariants", "parody", "character",
                              "tag", "artist", "group", "language",
                              "category", "series"]

            if isinstance(item, str):
                if column_name in target_columns:
                    items = item.split(";;;")
                    items = [_item for _item in items if len(item) > 0]
                    return items

            if isinstance(item, datetime):
                return item.strftime("%Y-%m-%dT%H:%M:%S")

            return item

        project = {column.name: f(getattr(project, column.name), column.name) for column in project.__table__.columns}

        return project

    def _prepare_to_update(self, project: dict) -> dict:
        def f(item, column_name):
            print(item)
            target_columns = ["lvariants", "parody", "character",
                              "tag", "artist", "group", "language",
                              "category", "series"]

            if isinstance(item, list):
                if column_name in target_columns:
                    return utils.list_to_str(item)

            if isinstance(item, str):
                # noinspection PyBroadException
                try:
                    return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S")
                except:
                    pass

            return item

        project = {key: f(val, key) for key, val in project.items()}

        project.pop("preview_path", None)
        project.pop("path", None)
        project.pop("id", None)
        project.pop("variants_view", None)

        project["search_body"] = make_search_body(project)

        return project

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
            })

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

        dict_project = self._to_dict(project)
        dict_project["variants_view"] = [variant.split(":")[1] for variant in dict_project["lvariants"]]
        # dict_project["variants_view"] = [variant for variant in dict_project["variants_view"] if len(variant) > 0]
        dict_project["path"] = self._get_project_path(project)
        dict_project["id"] = dict_project["_id"]
        dict_project["preview_path"] = self._get_project_preview_path(project)

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

    def add_project(self, project: dict):
        add_to_db(self.session, project)

    def count_item(self, item: str) -> list:
        result = defaultdict(int)

        items_strings = self.active_projects.with_entities(getattr(Project, item)).all()

        for items_string in items_strings:
            items = items_string[0].split(";;;")
            for item in items:
                result[item] += 1

        return sorted(result.items(), key=lambda x: x[1], reverse=True)

    def update_item(self, project: dict):
        project = self._prepare_to_update(project)
        print("UPDATE:")
        print(project)
        to_update = {getattr(Project, key): val for key, val in project.items()}
        self.session.query(Project).filter_by(_id=project["_id"]).update(to_update)
        self.session.commit()

    def clear_old_versions(self, target_version: int):
        self.session.query(Project).filter(Project.info_version < target_version).delete()
        self.session.commit()

    def delete_all_data(self):
        self.session.query(Project).delete()
        self.session.commit()

    def check_lids(self, lids: list) -> int:
        return self.all_projects.filter(Project.lid.in_(lids)).count()

    def create_priority(self, priority: list, non_priority: list):
        pool = self.get_project_by_lid(priority[0][0])
        pool["lid"] = f"pool_{utils.gen_lid()}"
        # upload_date = datetime.strftime(pool["upload_date"], "%Y-%m-%dT%H:%M:%S")

        for lid in non_priority:
            nproject = self.get_project_by_lid(lid[0])
            pool["tag"] = list(set(pool["tag"]) | set(nproject["tag"]))
            pool["language"] = list(set(pool["language"]) | set(nproject["language"]))
            pool["group"] = list(set(pool["group"]) | set(nproject["group"]))
            pool["artist"] = list(set(pool["artist"]) | set(nproject["artist"]))
            pool["series"] = list(set(pool["series"]) | set(nproject["series"]))
            pool["parody"] = list(set(pool["parody"]) | set(nproject["parody"]))

        self.add_project(pool)

        lids = [p[0] for p in (priority + non_priority)]

        self.all_projects.filter(Project.lid.in_(lids)).update({Project.active: False})
        self.session.commit()

    def update_pools_v(self, force: bool = False):
        variants = self.session.query(Project.lvariants).filter(Project.lvariants != None, Project.lvariants != "").distinct().all()
        variants = [variant[0] for variant in variants]
        for variant in variants:
            exist_pool = self.session.query(Project).filter(Project.lvariants == variant, Project.lid.icontains("pool_"))
            if (count := exist_pool.count()) > 0:
                if force is True or count > 1:
                    exist_pool.delete()
                    self.session.commit()
                else:
                    return

            variants_editor.edit(self, variant, separator=";;;")


def add_to_db(session, project: dict):
    def f(x):
        if isinstance(x, list):
            return ";;;".join(x)
        else:
            # noinspection PyBroadException
            try:
                d = datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')
                print(d)
                return d
            except:
                print(x)
                pass
            return x

    project = {k: f(v) for k, v in project.items()}

    # search_body = ";;;".join([project["lid"], project["source"], project["url"], project["downloader"],
    #                           project["title"], project["subtitle"], project["parody"], project["character"],
    #                           project["tag"], project["artist"], project["group"], project["language"],
    #                           project["category"], project["series"]])

    search_body = make_search_body(project)

    row = Project(info_version=project["info_version"],
                  lid=project["lid"],
                  lvariants=project["lvariants"],
                  source_id=project["source_id"],
                  source=project["source"],
                  url=project["url"],
                  downloader=project["downloader"],
                  title=project["title"],
                  subtitle=project["subtitle"],
                  upload_date=project["upload_date"],
                  preview=project["preview"],
                  parody=project["parody"],
                  character=project["character"],
                  tag=project["tag"],
                  artist=project["artist"],
                  group=project["group"],
                  language=project["language"],
                  category=project["category"],
                  series=project["series"],
                  pages=project["pages"],
                  dir_name=project["dir_name"],
                  lib=project["lib"],
                  search_body=search_body
                  )

    session.add(row)
    session.commit()


def make_search_body(project: dict):
    exclude = ["info_version", "lvariants", "url", "upload_date",
               "preview", "pages", "dir_name", "id",
               "_id", "search_body", "lid", "variants_view", "active"]

    search_body = ";;;"

    for k, v in project.items():
        if k not in exclude:
            items = v.split(";;;")
            for item in items:
                search_body += f"{k}:{item.lower()};;;"

    return search_body