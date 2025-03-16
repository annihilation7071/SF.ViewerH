from typing import Any
from pydantic import BaseModel, field_validator
from pathlib import Path
from pydantic_core.core_schema import ValidationInfo
from backend.utils import logger
from backend import utils
from backend.classes.templates import ProjectTemplate
import os
import re

log = logger.get_logger("Classes.files")


class ProjectInfoFileError(Exception):
    pass


class ProjectInfoFile(BaseModel):
    lid: str = None
    path: Path
    template: ProjectTemplate = None
    __path: Path = None
    __data: ProjectTemplate = None
    __backup: ProjectTemplate | None = None
    __status: str = None
    __saves: dict[str, ProjectTemplate] = None

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        log.debug(self.path)
        if os.path.exists(self.path) and self.template is not None:
            raise ProjectInfoFileError("File already exists. Do not provede template if file exists.")

        if self.template is None:
            self.__data = ProjectTemplate.load_from_json(self.path)
            self.__status = "ready"
        else:
            self.__data = self.template.model_copy(deep=True)
            self.__status = "not exist"

        self.__path = self.path
        self.__saves = {}
        self.lid = self.__data.lid

        del self.path
        del self.template

    # noinspection PyNestedDecorators
    @field_validator("path", mode="after")
    @classmethod
    def check_correct_path(cls, value: Path, info: ValidationInfo) -> Path:
        if re.fullmatch(r'^.*\\(sf\.viewer\\v_info.json)$', str(value)):
            return value
        else:
            e = ProjectInfoFileError(f"Path incorrected: {value}")
            log.exception(str(e), exc_info=e)
            raise e

    def set(self, data: ProjectTemplate) -> None:
        log.debug("")

        if self.__status == "ready":
            self.__backup = self.__data.model_copy(deep=True)
            self.__data = data.model_copy(deep=True)
            self.__status = "prepared_to_edit"
        elif self.__status == "not exist":
            e = ProjectInfoFileError("Unable set data to not existing project.")
            log.exception(e)
            raise e
        else:
            e = ProjectInfoFileError("Project info file already prepared to edit. Use rollback or commit to continue.")
            log.exception(str(e), exc_info=e)
            raise e

    def save(self, fs) -> None:
        log.debug("")
        if self.__status == "prepared_to_edit":

            utils.write_json(self.__path, self.__data, fs=fs)
            self.__backup = None
            self.__status = "ready"

        elif self.__status == "not exist":
            e = ProjectInfoFileError("Project info file not existing. Use write to create file.")
            log.exception(e)
            raise e
        else:
            e = ProjectInfoFileError("Project info not ready to commit. Use set prepare commit.")
            log.exception(str(e), exc_info=e)
            raise e

    def cancel_changes(self) -> None:
        log.debug("")
        if self.__status == "prepared_to_edit":
            self.__data = self.__backup
            self.__backup = None
            self.__status = "ready"
        else:
            if self.__status == "ready":
                e = ProjectInfoFileError(
                    "Project info not have data to change. Use set before rollback or commit to continue.")
            elif self.__status == "not exist":
                e = ProjectInfoFileError(
                    "Project not exist. Unable user rollback for non existing project.")
            else:
                e = ProjectInfoFileError("Unknown error.")
            log.exception(str(e), exc_info=e)
            raise e

    @property
    def data(self) -> ProjectTemplate:
        return self.__data.model_copy(deep=True)

    def create(self, fs, force: bool = False) -> None:
        log.debug("")
        if self.__status != "not exist":
            if self.__status == "ready" and force:
                os.makedirs(self.__path.parent, exist_ok=True)
                utils.write_json(self.__path, self.__data, fs=fs)
                log.info("File written successfully.")
            e = ProjectInfoFileError("Project must not exist to create file. Or use force to create file.")
            log.exception(e)
            raise e
        else:
            os.makedirs(self.__path.parent, exist_ok=True)
            utils.write_json(self.__path, self.__data, fs=fs)
            log.info("File written successfully.")

    @property
    def status(self):
        return self.__status
