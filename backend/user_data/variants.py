from backend.main_import import *
from backend.db import PoolVariant

log = logger.get_logger("User_data.variants")

_path = config.paths.user_data / "variants.json"


class Variants(BaseModel):
    version: int = 1
    date: datetime
    variants: list[PoolVariant] = []

    def save(self):
        log.debug("save")
        write_json(
            _path,
            self.model_dump_json()
        )

    @classmethod
    def load(cls):
        log.debug("load")
        if _path.exists():
            log.debug("load: file exists")
            return cls.model_validate(read_json(_path))
        else:
            log.debug("load: file does not exist")
            return cls(
                date=datetime(2000, 1, 1)
            )

