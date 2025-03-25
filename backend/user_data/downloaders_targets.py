from backend.main_import import *
from typing import Literal

if TYPE_CHECKING:
    from .libs import Lib, Libs

log = logger.get_logger("User_data.downloaders_targets")

_path = config.paths.user_data / "downloaders_targets.json"


class DownloaderTarget(BaseModel):
    site: Literal[
        "nhentai.net",
        "hitomi.la"
    ]
    lib: str

    @field_validator("lib", mode="after")
    @classmethod
    def check_lib(cls, lib: str) -> str:
        libs: 'Libs' = import_module(".libs", package="backend.user_data").Libs.load()
        libs_names = libs.get_names()
        if lib not in libs_names:
            raise ValidationError("Lib not exist")
        return lib


nhantai_target = DownloaderTarget(
    site="nhentai.net",
    lib="download-default-nhentai"
)

hitomila_target = DownloaderTarget(
    site="hitomi.la",
    lib="download-default-gallery-dl-hitomila"
)


class DownloadersTargets(BaseModel):
    nhentai: DownloaderTarget = nhantai_target
    hitomila: DownloaderTarget = hitomila_target

    def __getitem__(self, item) -> DownloaderTarget:
        for target in self.get_list_targets():
            if target.site == item:
                return target
        raise KeyError(item)

    @classmethod
    def load(cls) -> "DownloadersTargets":
        if _path.exists():
            return cls.model_validate(utils.read_json(_path))
        else:
            targets = cls()
            targets.save()
            return targets

    def save(self):
        utils.write_json(_path, self.model_dump_json())

    def get_list_targets(self) -> list[DownloaderTarget]:
        targets = list(self.model_dump().keys())
        return [getattr(self, key) for key in targets]

    def get_list_sites(self) -> list[str]:
        targets = self.get_list_targets()
        return [target.site for target in targets]