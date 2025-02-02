from backend.db import connect
from backend import cmdargs
from backend.classes.lib import Lib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.projects.projects import Projects
    from settingsUI import App


Session = connect.get_session()
args = cmdargs.args

# noinspection PyTypeChecker
projects: 'Projects' = None
# noinspection PyTypeChecker
libs: dict[str, Lib] = None
# noinspection PyTypeChecker
settingsUI: 'App' = None