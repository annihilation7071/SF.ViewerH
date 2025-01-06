from pydantic import BaseModel
from pathlib import Path


class Lib(BaseModel):
    name: str
    active: bool
    processor: str
    path: Path