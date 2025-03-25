from backend.main_import import *

_path = Path("./config.toml")


class ConfigServer(BaseModel):
    ip: str = "127.0.0.1"
    port: int = 1708


class ConfigLogger(BaseModel):
    app_log: bool = True
    app_log_level: str = "info"

    cutelog_log: bool = False
    cutelog_log_level: str = "debug"
    cutelog_ip: str = "127.0.0.1"
    cutelog_port: int = 19996

    fastapi_log: bool = True
    fastapi_log_level: str = "info"


class ConfigApp(BaseModel):
    renew_projects_when_startup: bool = True
    backup_variants_when_shutdown: bool = True


class ConfigPaths(BaseModel):
    user_data: Path = Path("./user_data")


class Config(BaseModel):
    server: ConfigServer = ConfigServer()
    logger: ConfigLogger = ConfigLogger()
    app: ConfigApp = ConfigApp()
    paths: ConfigPaths = ConfigPaths()

    @classmethod
    def load(cls) -> 'Config':
        if _path.exists():
            with open(_path, 'r', encoding="utf-8") as f:
                data = tomllib.loads(f.read())
            return cls.model_validate(data)
        else:
            return cls()


config = Config.load()