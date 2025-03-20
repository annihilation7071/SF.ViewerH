from backend.main_import import *
from . import item_editor
from . import variants_editor

log = logger.get_logger("Projects.editor.selector")


def edit(session: Session, fs: FSession, project: Project, edit_type: str, data: str, extra: dict = None):
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