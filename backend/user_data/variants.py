from backend.main_import import *

_path = dep.config.paths.user_data / "variants.json"


class Variants(BaseModel):
    date: datetime = datetime.now()
    data: list[PoolVariant] = []

    def save(self):
        utils.write_json(
            _path,
            self.model_dump_json()
        )

    @classmethod
    def load(cls):
        if _path.exists():
            return cls.model_validate(utils.read_json(_path))
        else:
            return cls()

