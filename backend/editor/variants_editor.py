from backend import dep
from backend.utils import tag_normalizer
from backend import logger
from backend.classes.projecte import ProjectE, ProjectEPool
from backend import utils
from typing import TYPE_CHECKING

log = logger.get_logger("VariantsEditor")

if TYPE_CHECKING:
    from backend.projects.cls import Projects


class VariantsEditorError(Exception):
    pass


def edit(project: ProjectE, data: str | list, separator: str = "\n"):
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
    with dep.Session() as session:
        for lid in lids:
            old_variants = old_variants | set(ProjectE.load_from_db(session, lid).lvariants)

    old_variants = list(old_variants)
    log.debug(f"Old variants: {old_variants}")

    old_lids = [variant.split(":")[0] for variant in old_variants]
    log.debug(f"Old lids: {old_lids}")

    with dep.Session() as session:
        # Check availability projects
        log.debug(f"Check availability old projects")
        if dep.projects.check_lids(session, old_lids) != len(old_lids):
            raise VariantsEditorError("Some projects not loaded")

        # Clear old variants (pools)
        log.debug(f"Clear old variants (pools)")
        unique_variants = [project]
        unique_check = {str(project.lvariants)}

        for lid in lids + old_lids:
            log.debug(f"Getting variants for {lid}")
            prjv = ProjectE.load_from_db(session, lid)
            if str(prjv.lvariants) not in unique_check:
                log.debug(f"{prjv}")
                unique_variants.append(prjv)
                unique_check.add(str(prjv.lvariants))

        for project in unique_variants:
            log.debug(f"Deleting pools with variant = {project.lvariants}")
            dep.projects.delete_pool(session, project.lvariants)

        old_projects = [ProjectE.load_from_db(session, lid) for lid in old_lids]

        updated_files = {}

        try:
            for t_project in old_projects:
                t_project.lvariants = []
                t_project.active = True
                infofile = t_project.update(session)
                updated_files[infofile.lid] = infofile

            # Stop if new variants not provided
            if len(variants) == 0:
                log.debug("New variants not provided. Stop variants_editor.edit")
                session.commit()
                return

            if len(priority) > 1:
                raise VariantsEditorError("Only one priority marker allowed")

            # Update data in info file and DB
            log.debug(f"Updating data in DB and file")
            target_projects = [ProjectE.load_from_db(session, lid) for lid in lids]

            for t_project in target_projects:
                log.debug(f"{t_project.lid}")
                t_project.lvariants = variants
                infofile = t_project.update_(session)
                if infofile.lid not in updated_files:
                    updated_files[infofile.lid] = infofile

            pool_lid = None
            # Create priority
            if len(priority) == 1:
                log.debug(f"Creating priority: {variants}")
                pool = ProjectEPool.create_pool(session, variants)

            session.commit()
            return pool.lid

        except Exception as e:
            log.exception(e)
            session.rollback()
            for file in updated_files.values():
                file.load_model("backup")
                file.commit()


