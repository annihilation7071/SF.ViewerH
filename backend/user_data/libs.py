import shutil

from backend.main_import import *
from typing import Literal

log = logger.get_logger("User_data.libs")

_path = config.paths.user_data / "libs.json"


class Lib(BaseModel):
    name: str
    processor: str
    path: Path
    active: bool = True
    category: Literal["user", "default"] = "user"


class Libs(BaseModel):
    version: int = 1
    libs: list[Lib] = []

    def __getitem__(self, key):
        for lib in self.libs:
            if lib.name == key:
                return lib
        raise KeyError(key)

    @classmethod
    def load(cls) -> "Libs":
        log.debug("load")
        if _path.exists():
            log.debug("load: file exists")
            libs_ = cls.model_validate(utils.read_json(_path))
        else:
            log.debug("load: file does not exist")
            libs_ = cls()

        libs_.update_defaults()
        libs_.add_old_format()
        libs_.save()
        return libs_

    def save(self):
        log.debug("save")
        utils.write_json(
            _path,
            self.model_dump_json()
        )

    def _get_index(self, name: str) -> int:
        for i in range(len(self.libs)):
            if self.libs[i].name == name:
                return i
        else:
            raise KeyError(f"Lib {name} not found")

    def update_defaults(self) -> None:
        default_libs = import_module(".default.libs", package="backend.user_data").default_libs

        exist = self.get_names()
        for default_lib in default_libs:
            if default_lib.name not in exist:
                self.libs.insert(0, default_lib)

    def add_old_format(self) -> None:
        old_path = Path("settings/libs")
        if not old_path.exists():
            return

        old = old_path.glob("*.json")
        exist = self.get_names()
        for old_lib_file in old:
            if str(old_lib_file).endswith("libs_default.json"):
                continue
            libdata = utils.read_json(old_lib_file)
            for key, value in libdata.items():
                if key not in exist:
                    self.libs.append(
                        Lib(
                            name=key,
                            processor=value["processor"],
                            path=Path(value["path"]),
                            active=value["active"],
                            category="user",
                        )
                    )

        shutil.rmtree(old_path)

    def get_names(self, only_active: bool = False, check_path: bool = False) -> list[str]:
        result = [
            lib for lib in self.libs if
            (only_active is False or lib.active is True)
        ]

        if check_path:
            for lib in result:
                if lib.path.exists() is False:
                    raise IOError(f"ERROR: libs dir {lib.path.absolute()} does not exist")

        result = [lib.name for lib in result]

        return result

    def add(self, lib: Lib) -> None:
        exist = self.get_names()
        if lib.name in exist:
            raise KeyError(f"Key {lib.name} already exists")
        self.libs.append(lib)

    def delete(self, id_: str) -> None:
        self.libs.pop(self._get_index(id_))
