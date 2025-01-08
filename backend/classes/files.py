from typing import Any
from pydantic import BaseModel
from pathlib import Path
from backend.logger_new import get_logger
from backend import utils
from backend.classes.templates import ProjectTemplate
import os

log = get_logger("classes.files")


class ProjectInfoFileError(Exception):
    pass


class ProjectInfoFile(BaseModel):
    path: Path
    template: ProjectTemplate = None
    __path: Path = None
    __data: ProjectTemplate = None
    __backup: ProjectTemplate | None = None
    __status: str = "ready"
    __saves: dict[str, ProjectTemplate] = None

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        if os.path.exists(self.path) and self.template is not None:
            raise ProjectInfoFileError("File already exists. Do not provede template if file exists.")

        if self.template is None:
            self.__data = ProjectTemplate.load_from_json(self.path)
        else:
            self.__data = self.template.model_copy(deep=True)

        self.__path = self.path
        self.__saves = {}

        del self.path
        del self.template

    def set(self, data: ProjectTemplate) -> None:
        log.debug("")

        if self.__status == "ready":
            self.__backup = self.__data.model_copy(deep=True)
            self.__data = data.model_copy(deep=True)
            self.__status = "prepared_to_edit"
        else:
            e = ProjectInfoFileError("Project info file already prepared to edit. Use rollback or commit to continue.")
            log.exception(str(e), exc_info=e)
            raise e

    def commit(self) -> None:
        log.debug("")
        if self.__status == "prepared_to_edit":
            try:
                utils.write_json(self.__path, self.__data)
                self.__backup = None
                self.__status = "ready"
            except Exception:
                utils.write_json(self.__path, self.__backup)
                log.exception("Failed to write project info file. Returning original data.")
                raise
        else:
            e = ProjectInfoFileError("Project info not ready to commit. Use set prepare commit.")
            log.exception(str(e), exc_info=e)
            raise e

    def rollback(self) -> None:
        log.debug("")
        if self.__status == "prepared_to_edit":
            self.__data = self.__backup
            self.__backup = None
            self.__status = "ready"
        else:
            e = ProjectInfoFileError("Project info not have data to change. Use set before rollback or commit to continue.")
            log.exception(str(e), exc_info=e)
            raise e

    def save_model(self, name: str) -> None:
        log.debug("")
        if self.__status == "ready":
            self.__saves[name] = self.__data
        else:
            raise ProjectInfoFileError("Save project able only when model is ready.")

    def load_model(self, name: str) -> None:
        log.debug("")
        if self.__status == "ready":
            self.set(self.__saves[name])
        elif self.__status == "prepared_to_edit":
            self.__data = self.__saves[name]

    @property
    def data(self) -> ProjectTemplate:
        return self.__data.model_copy(deep=True)





