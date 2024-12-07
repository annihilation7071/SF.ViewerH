import os
from backend import utils
from backend.db.connect import Project, get_session
from sqlalchemy import select, text, desc, asc, and_
from datetime import datetime


class Projects:
    def __init__(self, ppg: int = 60):
        self.session = get_session()
        self.libs = utils.read_libs()
        active_libs = [lib for lib, val in self.libs.items() if val["active"] is True]
        self.all_projects = self.session.query(Project).where(Project.lib.in_(active_libs)).order_by(desc(Project.upload_date))
        self.projects = self.all_projects
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
                    return item.split(";;;")

            if isinstance(item, datetime):
                return item.strftime("%Y-%m-%dT%H:%M:%S")

            return item

        project = {column.name: f(getattr(project, column.name), column.name) for column in project.__table__.columns}

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
            self.projects = self.all_projects
            return

        self.search = search
        search = search.split(",")
        search_query = [Project.search_body.icontains(item) for item in search]
        print(search)
        self.projects = self.session.query(Project).filter(and_(*search_query))
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

    def get_project_by_id(self, _id: int):
        project = self.projects.filter_by(_id=_id).first()
        dict_project = self._to_dict(project)
        dict_project["path"] = self._get_project_path(project)
        dict_project["id"] = dict_project["_id"]
        dict_project["preview_path"] = self._get_project_preview_path(project)

        return dict_project




