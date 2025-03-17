from backend.main_import import *


if TYPE_CHECKING:
    from backend.projects.projects import Projects
    from settingsUI import App
    from backend.classes import Lib

DB_VERSION = 5


# noinspection PyTypeChecker
Session: sqlmodel.Session = None
# noinspection PyTypeChecker
projects: 'Projects' = None
# noinspection PyTypeChecker
libs: dict[str, 'Lib'] = None
# noinspection PyTypeChecker
settingsUI: 'App' = None




class ConfigPaths(BaseModel):
    user_data: Path


class Config(BaseModel):
    paths: ConfigPaths


with open(Path("./config.toml"), encoding="utf-8") as f:
    config = Config.model_validate(
        tomllib.loads(f.read())
    )
