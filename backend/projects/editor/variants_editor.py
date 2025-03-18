from backend.main_import import *
from backend import dep
from backend.utils import *
from backend import logger
from backend.filesession import FileSession, FSession
from backend.db import Project, ProjectBase

log = logger.get_logger("Editor.variants")

if TYPE_CHECKING:
    from backend.projects.projects import Projects


class VariantsEditorError(Exception):
    pass


def edit(session: Session, fs: FSession, project: Project, data: str | list, separator: str = "\n"):
    log.debug(f"variant_editor.edit")
    log.debug(f"variants received: {data}")

    # New variants
    if isinstance(data, str):
        variants = data.split(separator)
    else:
        variants = data

    variants = [variant for variant in variants if variant != "" and variant.find(":") != -1]
    variants = tag_normalizer(variants, lower=False, ali=False)

    priority, non_priority = utils.separate_priority(variants)
    log.debug(f"Priority: {priority}")
    log.debug(f"Non priority: {non_priority}")

    # Sorting variants:
    # Priority first others sorting
    if len(priority) == 0:
        priority = [""]
    variants = [":".join(priority[0])] + [":".join(variant) for variant in sorted(non_priority, key=lambda x: x[1])]
    variants = [variant for variant in variants if len(variant) > 0]
    log.debug(f"Variants after sorting: {variants}")

    variants_count = len(variants)
    log.debug(f"New variants_count: {variants_count}")

    if variants_count == 1:
        raise VariantsEditorError("Too few variants")

    lids = [variant.split(":")[0] for variant in variants]
    log.debug(f"Lids: {lids}")
    log.debug(f"{project}")

    # Old variants
    old_variants = set()
    old_variants = old_variants | set(project.lvariants)

    for lid in lids:
        old_variants = old_variants | set(ProjectE.load_from_db(session, fs, lid).lvariants)

    old_variants = list(old_variants)
    log.debug(f"Old variants: {old_variants}")

    old_lids = [variant.split(":")[0] for variant in old_variants]
    log.debug(f"Old lids: {old_lids}")

    # Check availability projects
    log.debug(f"Check availability old projects")
    if dep.projects.check_lids_(session, old_lids) != len(old_lids):
        raise VariantsEditorError("Some projects not loaded")

    # Clear old variants (pools)
    log.debug(f"Clear old variants (pools)")
    unique_variants = [project]
    unique_check = {str(project.lvariants)}

    for lid in lids + old_lids:
        log.debug(f"Getting variants for {lid}")
        prjv = ProjectE.load_from_db(session, fs, lid)
        if str(prjv.lvariants) not in unique_check:
            log.debug(f"{prjv}")
            unique_variants.append(prjv)
            unique_check.add(str(prjv.lvariants))

    for project in unique_variants:
        log.debug(f"Deleting pools with variant = {project.lvariants}")
        dep.projects.delete_pool_(session, project.lvariants)

    old_projects = [ProjectE.load_from_db(session, fs, lid) for lid in old_lids]

    for t_project in old_projects:
        t_project.lvariants = []
        t_project.active = True
        infofile = t_project.update_(session, fs=fs)

    # Stop if new variants not provided
    if len(variants) == 0:
        log.debug("New variants not provided. Stop variants_editor.edit")
        return

    if len(priority) > 1:
        raise VariantsEditorError("Only one priority marker allowed")

    # Update data in info file and DB
    log.debug(f"Updating data in DB and file")
    target_projects = [ProjectE.load_from_db(session, fs, lid) for lid in lids]

    for t_project in target_projects:
        log.debug(f"{t_project.lid}")
        t_project.lvariants = variants
        infofile = t_project.update_(session, fs=fs)

    pool = None
    # Create priority
    if len(priority) == 1:
        log.debug(f"Creating priority: {variants}")
        pool = ProjectEPool.create_pool(session, fs, variants)

    if pool:
        log.debug(f"Returning: {pool.lid}")
        return pool.lid
