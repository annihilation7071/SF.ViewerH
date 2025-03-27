from backend.main_import import *
from typing import Literal

log = logger.get_logger("User_data.downloaders_settings")

_path = config.paths.user_data / "downloaders_settings.json"


class BaseDownloaderSettings(BaseModel):
    _downloaders: Union['DownloadersSettings', None] = None
    site: str | None
    name: str
    proxy: str | None = None
    user_agent: str | None = None
    cookies: str | None = None

    @field_validator("proxy", mode="after")
    @classmethod
    def chech_proxy(cls, v) -> str | None:
        if v is None:
            return None

        if validators.http_proxy(v):
            return v
        else:
            raise ValidationError(f"Invalid proxy format: {v}")

    def get_cookies(self):
        return self.cookies


general_downloader_settings = BaseDownloaderSettings(
    site=None,
    name="general",
    cookies="not_available"
)


class NHentaiDownloaderSettings(BaseDownloaderSettings):
    site: Literal["nhentai.net"] = "nhentai.net"
    cookies: str | None = None

    @field_validator("cookies", mode="after")
    @classmethod
    def check_cookies(cls, v: str) -> str | None:
        if v is None:
            return None

        if validators.cookies(v):
            return v
        elif v.endswith(".txt"):
            if Path(v).exists() is False:
                raise ValidationError(f"cookie file not found: {v}")
            cookies_dict = utils.load_cookies_from_file(Path(v))
            cookies = [f"{key}={val}" for key, val in cookies_dict.items()]
            cookies = "; ".join(cookies)
            return cookies
        else:
            raise ValidationError("Invalid cookies format")

    def get_proxy(self):
        if self.proxy:
            return self.proxy
        else:
            return self._downloaders.general.proxy

    def get_user_agent(self):
        if self.user_agent:
            return self.user_agent
        else:
            return self._downloaders.general.user_agent


nhentai_downloader_settings = NHentaiDownloaderSettings(name="nhentai")


class GalleryDLSettings(BaseDownloaderSettings):
    site: None | Literal[
        "nhentai.net",
        "hitomi.la"
    ]
    cookies: Path | str | None = None

    @field_validator("cookies", mode="after")
    @classmethod
    def check_cookies(cls, v: Path | str | None) -> Path | str | None:
        if v is None or v == "not_available":
            return v

        v = Path(v)
        if v.exists():
            return v
        else:
            raise ValidationError(f"Cookie file not found: {v}")

    def get_proxy(self):
        if self.proxy:
            return self.proxy
        elif self._downloaders.gallery_dl_general.proxy:
            return self._downloaders.gallery_dl_general.proxy
        else:
            return self._downloaders.general.proxy

    def get_user_agent(self):
        if self.user_agent:
            return self.user_agent
        elif self._downloaders.gallery_dl_general.user_agent:
            return self._downloaders.gallery_dl_general.user_agent
        else:
            return self._downloaders.general.user_agent


gallery_dl_general_downloader_settings = GalleryDLSettings(
    site=None,
    name="gallery-dl-general",
    cookies="not_available"
)

gallery_dl_nhentai_downloader_settings = GalleryDLSettings(
    site="nhentai.net",
    name="gallery-dl-(nhentai.net)"
)

gallery_dl_hitomila_downloader_settings = GalleryDLSettings(
    site="hitomi.la",
    name="gallery-dl-(hitomi.la)"
)


class DownloadersSettings(BaseModel):
    general: BaseDownloaderSettings = general_downloader_settings
    nhentai: NHentaiDownloaderSettings = nhentai_downloader_settings
    gallery_dl_general: GalleryDLSettings = gallery_dl_general_downloader_settings
    gallery_dl_nhentai: GalleryDLSettings = gallery_dl_nhentai_downloader_settings
    gallery_dl_hitomila: GalleryDLSettings = gallery_dl_hitomila_downloader_settings

    def get_list_downloaders(self) -> list[BaseDownloaderSettings]:
        downloaders = list(self.model_dump().keys())
        return [getattr(self, key) for key in downloaders]

    def get_gallery_dl_downloader_by_site_name(self, site_name: str) -> GalleryDLSettings:
        for key in self.model_dump().keys():
            if key.lower().startswith("gallery_dl"):
                downloader_ = getattr(self, key)
                if downloader_.site == site_name:
                    return downloader_
        raise KeyError(f"{site_name} not found")

    @classmethod
    def load(cls) -> "DownloadersSettings":
        if _path.exists():
            settings = cls.model_validate(read_json(_path))
        else:
            settings = cls()
            settings.save()

        downloaders = settings.get_list_downloaders()
        for downloader in downloaders:
            downloader._downloaders = settings

        return settings

    def save(self):
        write_json(_path, self.model_dump_json())
