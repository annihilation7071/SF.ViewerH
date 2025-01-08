from backend.db import connect
from backend import cmdargs

Session = connect.get_session()
args = cmdargs.args