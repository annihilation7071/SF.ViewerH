from backend.main_import import *
from ..libs import Lib

default_libs = [
    Lib(
        name="download-default-nhentai",
        processor="nhentai",
        path=Path("downloads\\default-nhentai"),
        active=True,
        category="default",
    ),
    Lib(
        name="download-default-gallery-dl-hitomila",
        processor="gallery-dl-hitomila",
        path=Path("downloads\\default-gallery-dl-hitomila"),
        active=True,
        category="default",
    ),
    Lib(
        name="download-default-gallery-dl-nhentai",
        processor="gallery-dl-nhentai",
        path=Path("downloads\\default-gallery-dl-nhentai"),
        active=False,
        category="default",
    )
]