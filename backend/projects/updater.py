from backend import dep
from pathlib import Path
import os
from importlib import import_module
from backend import utils, cmdargs
from backend.logger_new import get_logger
from backend.projects.cls import Projects
from backend.upgrade import vinfo
from backend.processors import general as general
import json
from dateutil import parser
from backend.classes.templates import ProjectTemplate, ProjectTemplateDB
from backend.classes.files import ProjectInfoFile

log = get_logger("putils")


def update_projects(projects: Projects) -> None:
    log.debug("update_projects")
    log.info("Updating projects ...")
    libs = utils.read_libs()

    for lib_name, lib_data in libs.items():
        if lib_data.active is False:
            continue

        processor_name = lib_data.processor

        log.info(f"Checking {lib_name} ...")
        if cmdargs.args.reindex is True:
            log.warning(f"Deleting all data...")
            cmdargs.args.reindex = False
            with dep.Session() as session:
                projects.delete_all_data(session)
                session.commit()

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info_example = json.load(f)

        with dep.Session() as session:
            projects.clear_old_versions(session, v_info_example["info_version"])
            session.commit()

        processor = import_module(f"backend.processors.{lib_data.processor}")

        path = lib_data.path
        log.debug(f"Lib path: {path}")
        dirs = get_dirs(path, processor.meta_file)
        log.debug(f"Dirs in lib path: {dirs}")

        dirs_not_in_db, dirs_not_exist = check_dirs(lib_name, dirs)
        log.debug(f"dirs_not_in_db: {len(dirs_not_in_db)}")
        log.debug(dirs_not_in_db)
        log.debug(f"dirs_not_exist: {len(dirs_not_exist)}")
        log.debug(dirs_not_exist)

        if len(dirs_not_exist) > 0:
            log.info(f"Deleting not exist projects...")

        with dep.Session() as session:
            for dir in dirs_not_exist:
                log.debug(f"Deleting {dir} ...")
                projects.delete_by_dir_and_lib(session, dir, lib_name)
            session.commit()

        if len(dirs_not_in_db) > 0:
            log.info(f"Adding new projects...")

        with dep.Session() as session:
            for dir in dirs_not_in_db:
                log.debug(f"Adding {dir} ...")
                project_path = path / dir

                project = get_project_info(project_path)
                if project is None:
                    log.debug(f"vinfo for {dir} not found...")
                    log.info(f"Preparing project {dir}...")
                    general.make_v_info(project_path, processor_name)
                    project = get_project_info(project_path)

                project_to_db = ProjectTemplateDB(
                    lib=lib_name,
                    dir_name=dir,
                    **project.model_dump()
                )

                log.debug(project_to_db)

                project_to_db.add_to_db(session)
            session.commit()


def get_dirs(path: Path, meta_file: str) -> list[str]:
    log.debug("get_dirs")
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if os.path.exists(os.path.join(path, file) + f"/{meta_file}"):
            dirs.append(file)
    return dirs


def check_dirs(lib_name: str, dirs: list[str]) -> tuple:
    log.debug("check_dirs")
    exist_dirs = set(dirs)
    with dep.Session() as session:
        dirs_in_db = set(dep.projects.get_dirs(session, lib_name))

    log.debug(f"dirs found in db: {dirs_in_db}")

    dirs_not_in_db = exist_dirs - dirs_in_db

    dirs_not_exist = dirs_in_db - exist_dirs

    return dirs_not_in_db, dirs_not_exist


def get_project_info(path: Path) -> ProjectTemplate | None:
    log.debug("get_v_info")
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info_example = json.load(f)

    v_info_path = path / "sf.viewer/v_info.json"

    if os.path.exists(v_info_path):

        project_infofile = ProjectInfoFile(path=v_info_path)

        project_info = project_infofile.data

        if project_info.info_version == v_info_example["info_version"]:
            return project_info
        else:
            project_info = vinfo.upgrade(path, project_info)

            project_infofile.set(project_info)
            project_infofile.commit()

            return get_project_info(path)

    else:
        return None
