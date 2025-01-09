from backend.db import connect
from backend import cmdargs
from backend.projects.cls import Projects
from backend.classes.lib import Lib

Session = connect.get_session()
args = cmdargs.args

# noinspection PyTypeChecker
projects: Projects = None
# noinspection PyTypeChecker
libs: dict[str, Lib] = None