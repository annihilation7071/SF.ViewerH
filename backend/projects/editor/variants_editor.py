from backend.main_import import *

log = logger.get_logger("Projects.editor.variants_editor")

if TYPE_CHECKING:
    from backend.projects.projects import Projects


class VariantsEditorError(Exception):
    pass


def edit(session: Session, fs: FSession, project: Project, data: str | list, separator: str = "\n"):
    log.debug(f"variant_editor.edit")
    log.debug(f"variants received: {data}")


