from backend.main_import import *

log = logger.get_logger("Classes.lib")


class Lib(BaseModel):
    libfile: Path
    name: str
    active: bool
    processor: str
    path: Path

    def save(self):
        log.debug(f"Saving {self.name}")

        file = utils.read_json(self.libfile)

        file[self.name]["active"] = self.active
        file[self.name]["processor"] = self.processor
        file[self.name]["path"] = str(self.path)

        utils.write_json(self.libfile, file)

    def delete(self):
        log.debug(f"Delete {self.name}")

        file = utils.read_json(self.libfile)

        file.pop(self.name)

        if len(file) > 0:
            utils.write_json(self.libfile, file)
        else:
            os.remove(self.libfile)

    def create(self):
        log.debug(f"Creating {self.name}")

        if self.libfile.exists():
            file = utils.read_json(self.libfile)

            file[self.name] = {
                    "active": self.active,
                    "processor": self.processor,
                    "path": str(self.path)
                }

        else:
            file = {
                self.name: {
                    "active": self.active,
                    "processor": self.processor,
                    "path": str(self.path)
                }
            }

        utils.write_json(self.libfile, file)