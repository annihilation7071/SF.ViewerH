from backend.main_import import *

log = logger.get_logger("Editor.item")


class ItemEditorError(Exception):
    pass


edit_types = {
    "edit-tags": "tag",
    "edit-series": "series"
}


def edit(session: Session, fs: FSession, project: Project, edit_type: str, data: str) -> str:
    log.debug("edit")
    log.debug(f"edit: type: {edit_type}")
    log.debug(f"edit: data: {data}")

    if edit_type not in edit_types:
        raise ItemEditorError(f"edit_type: {edit_type} not supported")

    items = data.split("\n")
    items = [item for item in items if item != ""]
    items = utils.tag_normalizer(items)
    log.debug(f"edit: normalized items: {items}")

    if project.is_pool:
        log.debug(f"edit: project is a pool.")
        return _edit_pool(session, fs, project, edit_type, items)

    setattr(project, edit_types[edit_type], items)

    project.project_update_project(session, fs=fs)

    if pool_lid := project.has_pool:
        log.debug(f"edit: project has pool: {pool_lid}")
        pool = session.scalar(
            select(Project).where(
                Project.lid == pool_lid
            )
        )

        pool.pool_sync_(session)

    return project.lid


def _edit_pool(session: Session, fs: FSession, project: Project, edit_type: str, data: str) -> str:
    log.debug("_edit_pool")

    field = edit_types[edit_type]

    original_data = set(getattr(project, field))
    log.debug(f"_edit_pool: original_data: {original_data}")

    deleted = original_data - set(data)
    log.debug(f"_edit_pool: deleted: {deleted}")

    added = set(data) - original_data
    log.debug(f"_edit_pool: added: {added}")

    projects_lids = [variant.project for variant in project.variants]

    projects = session.scalars(
        select(Project).where(
            Project.lid.in_(projects_lids)
        )
    )

    for project_ in projects:
        old_data = set(getattr(project_, field))
        new_data = old_data - deleted
        new_data = new_data | added
        setattr(project_, field, list(new_data))

    return project.lid
