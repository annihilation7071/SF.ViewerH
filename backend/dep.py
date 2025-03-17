from backend.main_import import *


if TYPE_CHECKING:
    from backend.projects.projects import Projects
    from settingsUI import App
    from backend.classes import Lib

DB_VERSION = 4

# noinspection PyTypeChecker
Session: sqlmodel.Session = None
# noinspection PyTypeChecker
projects: 'Projects' = None
# noinspection PyTypeChecker
libs: dict[str, 'Lib'] = None
# noinspection PyTypeChecker
settingsUI: 'App' = None


def init():
    global projects
    global libs
    global settingsUI
    global Session

    libs = utils.read_libs()
    Session = connect.get_session()
