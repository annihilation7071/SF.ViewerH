from backend.main_import import *

if TYPE_CHECKING:
    from backend.projects.projects import Projects
    from settingsUI import App
    from backend.user_data import Libs

# noinspection PyTypeChecker
Session: sqlmodel.Session = None
# noinspection PyTypeChecker
projects: 'Projects' = None
# noinspection PyTypeChecker
libs: 'Libs' = None
# noinspection PyTypeChecker
settingsUI: 'App' = None

