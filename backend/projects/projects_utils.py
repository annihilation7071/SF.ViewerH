from backend.main_import import *
from backend import processors
from backend import upgrade


if TYPE_CHECKING:
    from backend.projects.projects import Projects

log = logger.get_logger("Projects.updater")


def update_projects(session: Session, fs: FSession) -> None:
    log.debug("update_projects")
    log.info("Updating projects ...")

    if cmdargs.reindex is True:
        log.warning(f"Deleting all data...")
        cmdargs.reindex = False
        dep.projects.delete_all_data_(session)

    for lib in dep.libs.values():
        if lib.active is False:
            continue

        processor_name = lib.processor

        log.info(f"Checking {lib.name} ...")

        with open("./backend/v_info.json", "r", encoding="utf-8") as f:
            v_info_example = json.load(f)

        dep.projects.clear_old_versions_(session, dep.DB_VERSION)

        processor = import_module(f"backend.processors.{lib.processor}")

        path = lib.path
        log.debug(f"Lib path: {path}")
        dirs = get_dirs(path, processor.meta_file)
        log.debug(f"Dirs in lib path: {dirs}")

        dirs_not_in_db, dirs_not_exist = check_dirs(session, lib, dirs)
        log.debug(f"dirs_not_in_db: {len(dirs_not_in_db)}")
        log.debug(dirs_not_in_db)
        log.debug(f"dirs_not_exist: {len(dirs_not_exist)}")
        log.debug(dirs_not_exist)

        for dir in dirs_not_exist:
            log.info(f"Deleting not exist projects...")
            log.debug(f"Deleting {dir} ...")
            dep.projects.delete_by_dir_and_lib_(session, dir, lib)

        if len(dirs_not_in_db) > 0:
            log.info(f"Adding new projects...")

        for dir_name in dirs_not_in_db:
            project_path = path / dir_name
            add_project_dir_to_db(session, fs, lib, project_path, processor_name)


def add_project_dir_to_db(session: Session, fs: FSession, lib: Lib, project_path: Path, processor_name: str) -> None:
    log.debug(f"Adding {project_path.name} ...")

    project = get_project_info(session, fs, project_path)
    if project is None:
        log.debug(f"vinfo for {project_path.name} not found...")
        log.info(f"Preparing project {project_path.name} ...")
        processors.make_v_info(session, fs, project_path, processor_name)
        project = get_project_info(session, fs, project_path)

    project_to_db = Project(
        lib=lib.name,
        dir_name=project_path.name,
        **project.model_dump()
    )

    log.debug(project_to_db)

    project_to_db.project_add_to_db(session)


def get_dirs(path: Path, meta_file: str) -> list[str]:
    log.debug("get_dirs")
    dirs = []
    if os.path.exists(path) is False:
        os.makedirs(path)
    files = os.listdir(path)
    for file in files:
        if (path / file / f"{meta_file}").exists():
            dirs.append(file)
    return dirs


def check_dirs(session: Session, lib: Lib, dirs: list[str]) -> tuple:
    log.debug("check_dirs")
    exist_dirs = set(dirs)

    dirs_in_db = set(dep.projects.get_dirs_(session, lib.name))

    log.debug(f"dirs found in db: {dirs_in_db}")

    dirs_not_in_db = exist_dirs - dirs_in_db

    dirs_not_exist = dirs_in_db - exist_dirs

    return dirs_not_in_db, dirs_not_exist


def get_project_info(session: Session, fs: FSession, path: Path) -> ProjectBase | None:
    log.debug("get_project_info")
    with open('./backend/v_info.json', 'r', encoding='utf-8') as f:
        v_info_example = json.load(f)

    v_info_path = path / "sf.viewer/v_info.json"

    if os.path.exists(v_info_path):

        project_info = ProjectBase.project_file_load(v_info_path)
        project_info._path = path

        if project_info.info_version == ProjectBase(lid="temp").info_version:
            return project_info
        else:
            project_info = upgrade.vinfo.upgrade(session, path, project_info)

            project_info.prolect_file_save(fs=fs)

            project_info = get_project_info(session, fs, path)

            if project_info is None:
                raise IOError("Unexpected error.")

            return project_info

    else:
        return None
