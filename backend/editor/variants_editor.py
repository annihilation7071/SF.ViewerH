from backend.utils import tag_normalizer
from backend.editor import eutils
from backend.logger import log


def edit(projects, data: str | list, project: dict, separator: str = "\n"):
    log(f"Project received by project_editor: {project['lid']}", "variants-3")
    # New variants
    if isinstance(data, str):
        variants = data.split(separator)
    else:
        variants = data

    variants = [variant for variant in variants if variant != "" and variant.find(":") != -1]
    variants = tag_normalizer(variants, lower=False, ali=False)
    log(f"Variants: {variants}", "variants-3")

    variants_count = len(variants)

    if variants_count < 2:
        raise Exception("Too few variants")

    lids = [variant.split(":")[0] for variant in variants]

    # Old variants
    old_variants = project["lvariants"]
    log(f"Old variants: {old_variants}", "variants-3")
    old_lids = [variant.split(":")[0] for variant in old_variants]

    # Check availability projects
    if projects.check_lids(lids) != len(lids) or projects.check_lids(old_lids) != len(old_lids):
        raise Exception("Some projects not loaded")
    log(f"Availability checked", "variants-3")

    # Clear old variants
    projects.delete_pool(old_variants)

    old_projects = [projects.get_project_by_lid(lid) for lid in old_lids]

    for t_project in old_projects:
        eutils.update_data(projects, t_project, ["lvariants", "active"], [[], True])

    # Find priority project
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

    log(f"Priority: {priority}", "variants-3")
    log(f"Non priority: {non_priority}", "variants-3")

    if len(priority) > 1:
        raise Exception("Only one priority marker allowed")

    # Sorting variants:
    # Priority first others sorting
    variants = [":".join(priority[0])] + [":".join(variant) for variant in sorted(non_priority, key=lambda x: x[1])]
    variants = [variant for variant in variants if len(variant) > 0]
    log(f"Variants after sorting: {variants}", "variants-3")

    # Update data in info file and DB
    target_projects = [projects.get_project_by_lid(lid) for lid in lids]

    for t_project in target_projects:
        eutils.update_data(projects, t_project, "lvariants", variants)

    # Create priority
    if len(priority) == 1:
        log(f"Start creating priority", "variants-3")
        return projects.create_priority(priority, non_priority)

    return