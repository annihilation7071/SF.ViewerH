from typing import Any

from pydantic import BaseModel, field_validator, ValidationError
import re
import http.cookiejar
from pathlib import Path
from backend import utils
from backend.modules import logger
from collections import defaultdict

log = logger.get_logger("Downloader.settings")


class DSettings(BaseModel):
    proxy: str | None
    user_agent: str | None


    @field_validator("proxy", mode="after")
    @classmethod
    def check_proxy(cls, v: str) -> str:
        math = re.fullmatch(r"^http(s)?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d*$", v)
        if math:
            return v
        else:
            raise ValidationError("Invalid proxy format")

    def model_post_init(self, __context: Any) -> None:
        log.debug(self)


class NhentaiSettings(DSettings):
    cookies: str | None

    @field_validator("cookies", mode="after")
    @classmethod
    def check_cookies(cls, v: str) -> str:
        matn = re.fullmatch(r"([a-zA-Z_\.\d\-\|]*=[a-zA-Z_\.\d\-\|]*)(; )?", v)
        if matn:
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

    @classmethod
    def load(cls):
        settings = BaseSettings.load()

        proxy = settings["nhentai"].proxy
        if proxy is None:
            proxy = settings["general"].proxy

        user_agent = settings["nhentai"].user_agent
        if user_agent is None:
            user_agent = settings["general"].user_agent

        cookies = settings["nhentai"].cookies

        return cls(
            proxy=proxy,
            user_agent=user_agent,
            cookies=cookies
        )


class GalleryDLSettings(DSettings):
    site: str
    cookies: Path | None

    @classmethod
    def load(cls, site: str):
        settings = BaseSettings.load()

        proxy = settings[f"gallery-dl-({site})"].proxy
        if proxy is None:
            proxy = settings[f"gallery-dl-general"].proxy
        if proxy is None:
            proxy = settings[f"general"].proxy

        user_agent = settings[f"gallery-dl-({site})"].user_agent
        if user_agent is None:
            user_agent = settings[f"gallery-dl-general"].user_agent
        if user_agent is None:
            user_agent = settings[f"general"].user_agent

        cookies = settings[f"gallery-dl-({site})"].cookies
        if cookies is not None:
            cookies = Path(cookies)
            if cookies.exists() is False:
                raise ValidationError(f"cookie file not found: {cookies}")

        return cls(
            site=site,
            proxy=proxy,
            user_agent=user_agent,
            cookies=cookies
        )


class BaseSettings(BaseModel):
    _downloader: str
    proxy: str | None
    user_agent: str | None
    cookies: Path | str | None

    @classmethod
    def load(cls) -> dict[str, 'BaseSettings']:
        data: dict[str, dict[str, str]] = utils.read_json(Path("./settings/download/settings.json"))
        data = {key: defaultdict(lambda: "N/A", val) for key, val in data.items()}

        result = {}

        for key in data.keys():
            result[key] = cls(
                _downloader=key,
                proxy=data[key]["proxy"],
                user_agent=data[key]["user_agent"],
                cookies=data[key]["cookies"]
            )

        return result

    def save(self):
        data = dict[str, dict[str, str]] = utils.read_json(Path("./settings/download/settings.json"))

        atr = list(self.model_dump())

        changed = False

        for key, value in data[self._downloader].items():
            if getattr(self, key) != value:
                changed = True
                break

        if changed:
            for key in atr:
                data[self._downloader][key] = getattr(self, key)

            utils.write_json(Path("./settings/download/settings.json"), data)
            log.debug(f"Changes were saved: {self._downloader}")



