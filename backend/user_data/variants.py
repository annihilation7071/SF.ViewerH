from backend.main_import import *

log = logger.get_logger("User_data.variants")

_path = dep.config.paths.user_data / "variants.json"


class Variants(BaseModel):
    version: int = 1
    date: datetime
    variants: list[PoolVariant] = []

    def save(self):
        log.debug("save")
        utils.write_json(
            _path,
            self.model_dump_json()
        )

    @classmethod
    def load(cls):
        log.debug("load")
        if _path.exists():
            log.debug("load: file exists")
            return cls.model_validate(utils.read_json(_path))
        else:
            log.debug("load: file does not exist")
            return cls(
                date=datetime(2000, 1, 1)
            )

