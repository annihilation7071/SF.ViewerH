from pydantic import BaseModel
from pathlib import Path
from backend import utils


class Lib(BaseModel):
    libfile: Path
    name: str
    active: bool
    processor: str
    path: Path

    def save(self):
        file = utils.read_json(self.libfile)

        file[self.name]["active"] = self.active
        file[self.name]["processor"] = self.processor
        file[self.name]["path"] = str(self.path)

        utils.write_json(self.libfile, file)

    def delete(self):
        file = utils.read_json(self.libfile)

        file.pop(self.name)

        utils.write_json(self.libfile, file)

    def create(self):
        lib = {
            "name": {
                "active": self.active,
                "processor": self.processor,
                "path": str(self.path)
            }
        }

        utils.write_json(self.libfile, lib)