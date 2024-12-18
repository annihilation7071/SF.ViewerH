from backend.utils import tag_normalizer
from backend.editor import eutils
from backend.logger import log


def edit(projects, data: str | list, lvariants: str | list, separator: str = "\n"):

    # New variants
    if isinstance(data, str):
        variants = data.split(separator)
    else:
        variants = data

    variants = [variant for variant in variants if variant != "" and variant.find(":") != -1]
    variants = tag_normalizer(variants, lower=False, ali=False)

    variants_count = len(variants)

    if variants_count < 2:
        raise Exception("Too few variants")

    lids = [variant.split(":")[0] for variant in variants]

    # Old variants
    if isinstance(data, str):
        old_variants = lvariants.split("\n")
    else:
        old_variants = lvariants

    print(old_variants)
    old_variants = [variant for variant in old_variants if variant != "" and variant.find(":") != -1]
    old_variants = tag_normalizer(old_variants, lower=False, ali=False)
    old_lids = [variant.split(":")[0] for variant in old_variants]

    # Check availability projects
    if projects.check_lids(lids) != len(lids) or projects.check_lids(old_lids) != len(old_lids):
        raise Exception("Some projects not loaded")

    # Clear old variants
    projects.delete_pool(old_variants)

    old_projects = [projects.get_project_by_lid(lid) for lid in old_lids]

    for t_project in old_projects:
        eutils.update_data(projects, t_project, "lvariants", [])

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

    if len(priority) > 1:
        raise Exception("Only one priority marker allowed")

    # Sorting variants:
    # Priority first others sorting
    variants = [":".join(priority[0])] + [":".join(variant) for variant in sorted(non_priority)]
    variants = [variant for variant in variants if len(variant) > 0]

    # Update data in info file and DB
    target_projects = [projects.get_project_by_lid(lid) for lid in lids]

    for t_project in target_projects:
        eutils.update_data(projects, t_project, "lvariants", variants)

    # Create priority
    if len(priority) == 1:
        return projects.create_priority(priority, non_priority)

    return