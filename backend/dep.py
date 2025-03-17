from backend.main_import import *


if TYPE_CHECKING:
    from backend.projects.projects import Projects
    from settingsUI import App

Session: Session = connect.get_session()

# noinspection PyTypeChecker
projects: 'Projects' = None
# noinspection PyTypeChecker
libs: dict[str, Lib] = utils.read_libs()
# noinspection PyTypeChecker
settingsUI: 'App' = None

