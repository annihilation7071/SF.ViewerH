from backend.main_import import *


class ConfigPaths(BaseModel):
    user_data: Path


class Config(BaseModel):
    paths: ConfigPaths

    @classmethod
    def load(cls) -> 'Config':
        with open(Path("./config.toml"), mode="r", encoding="utf-8") as f:
            config_ = Config.model_validate(
                tomllib.loads(f.read())
            )
        return config_


config = Config.load()
