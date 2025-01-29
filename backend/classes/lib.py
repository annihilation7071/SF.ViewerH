from pydantic import BaseModel
from pathlib import Path


class Lib(BaseModel):
    libfile: Path
    name: str
    active: bool
    processor: str
    path: Path