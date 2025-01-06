from backend.utils import tag_normalizer
from backend.logger_new import get_logger
from backend.classes.projecte import ProjectE
from typing import TYPE_CHECKING

log = get_logger("VariantsEditor")

if TYPE_CHECKING:
    from backend.projects.cls import Projects


class VariantsEditorError(Exception):
    pass


def edit(projects: 'Projects', project: ProjectE, data: str | list, separator: str = "\n"):
    log.debug(f"variant_editor.edit")
    log.debug(f"")

    # New variants
    if isinstance(data, str):
        variants = data.split(separator)
    else:
        variants = data

    variants = [variant for variant in variants if variant != "" and variant.find(":") != -1]
    variants = tag_normalizer(variants, lower=False, ali=False)
    log.debug(f"New variants: {variants}")

    variants_count = len(variants)
    log.debug(f"New variants_count: {variants_count}")

    if variants_count == 1:
        raise VariantsEditorError("Too few variants")

    lids = [variant.split(":")[0] for variant in variants]
    log.debug(f"Lids: {lids}")

    # Old variants
    old_variants = set()
    old_variants = old_variants | set(project["lvariants"])
    for lid in lids:
        old_variants = old_variants | set(projects.get_project_by_lid(lid)["lvariants"])
    old_variants = list(old_variants)
    log.debug(f"Old variants: {old_variants}")

    old_lids = [variant.split(":")[0] for variant in old_variants]
    log.debug(f"Old lids: {old_lids}")

    # Check availability projects
    log.debug(f"Check availability projects")
    if projects.check_lids(lids) != len(lids) or projects.check_lids(old_lids) != len(old_lids):
        raise VariantsEditorError("Some projects not loaded")

    # Clear old variants (pools)
    log.debug(f"Clear old variants (pools)")
    unique_variants = [project.lvariants]
    unique_check = {str(project.lvariants)}

    for lid in lids + old_lids:
        log.debug(f"Getting variants for {lid}")
        prjv = projects.get_project_by_lid(lid).lvariants
        if str(prjv) not in unique_check:
            log.debug(f"{prjv}")
            unique_variants.append(prjv)
            unique_check.add(str(prjv))

    for variant in unique_variants:
        log.debug(f"Deleting pools with variant = {variant}")
        projects.delete_pool(variant)

    old_projects = [projects.get_project_by_lid(lid) for lid in old_lids]

    for t_project in old_projects:
        t_project.lvariants = []
        t_project.active = True
        t_project.update_db()
        t_project.update_vinfo()

    # Stop if new variants not provided
    if len(variants) == 0:
        log.debug("New variants not provided. Stop variants_editor.edit")
        return

    # Find priority project
    priority, non_priority = separate_priority(variants)
    log.debug(f"Priority: {priority}")
    log.debug(f"Non priority: {non_priority}")

    if len(priority) > 1:
        raise VariantsEditorError("Only one priority marker allowed")

    # Sorting variants:
    # Priority first others sorting
    variants = [":".join(priority[0])] + [":".join(variant) for variant in sorted(non_priority, key=lambda x: x[1])]
    variants = [variant for variant in variants if len(variant) > 0]
    log.debug(f"Variants after sorting: {variants}")

    # Update data in info file and DB
    log.debug(f"Updating data in DB and file")
    target_projects = [projects.get_project_by_lid(lid) for lid in lids]

    for t_project in target_projects:
        log.debug(f"{t_project.lid}")
        t_project.lvariants = variants
        t_project.update_db()
        t_project.update_vinfo()

    # Create priority
    if len(priority) == 1:
        log.debug(f"Creating priority: {variants}")
        return projects.create_priority(priority, non_priority)

    return


def separate_priority(variants: list) -> tuple[list, list]:
    priority = []
    non_priority = []
    for variant in variants:
        variant = variant.split(":")
        if len(variant) == 3:
            if variant[2] in ["priority", "p"]:
                priority.append(variant)
            else:
                raise Exception(f"Unknown marker {variant[2]}")
        else:
            non_priority.append(variant)

    return priority, non_priority