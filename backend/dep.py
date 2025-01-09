from backend.db import connect
from backend import cmdargs
from backend.projects.cls import Projects

Session = connect.get_session()
args = cmdargs.args
# noinspection PyTypeChecker
projects: Projects = None