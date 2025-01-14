from backend.editor import item_editor, variants_editor
from backend.classes.projecte import ProjectE
from backend import logger
from sqlalchemy.orm import Session
from backend.modules.filesession import FSession

log = logger.get_logger("Editor.selector")


def edit(session: Session, fs: FSession, project: ProjectE, edit_type: str, data: str, extra: dict = None):
    log.debug("edit")
    match edit_type:
        case "edit-tags" | "edit-series":
            log.debug("edit-tags")
            return item_editor.edit(session, fs, project, edit_type, data)
        case "edit-variants":
            log.debug("edit-variants")
            return variants_editor.edit(session, fs, project, data)
        case _:
            log.error(f"invalid edit type: {edit_type}")