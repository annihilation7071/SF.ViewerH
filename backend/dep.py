from backend.main_import import *
from backend.utils import *
from backend import cmdargs
from backend.classes.lib import Lib
from backend.db.connect import get_session


if TYPE_CHECKING:
    from backend.projects.projects import Projects
    from settingsUI import App

Session: Session = get_session()
args = cmdargs.args

# noinspection PyTypeChecker
projects: 'Projects' = None
# noinspection PyTypeChecker
libs: dict[str, Lib] = utils.read_libs()
# noinspection PyTypeChecker
settingsUI: 'App' = None

