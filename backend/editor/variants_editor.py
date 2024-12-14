from backend.utils import tag_normalizer
from backend.editor import eutils


def edit(projects, data: str, separator: str = "\n"):
    print("edit-variants")

    variants = data.split(separator)
    variants = [variant for variant in variants if variant != "" and variant.find(":") != -1]
    variants = tag_normalizer(variants, lower=False, ali=False)
    print(variants)

    if len(variants) < 2:
        raise Exception("Too few variants")

    lids = [variant.split(":")[0] for variant in variants]

    if projects.check_lids(lids) != len(lids):
        raise Exception("Some projects not loaded")

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

    target_projects = [projects.get_project_by_lid(lid) for lid in lids]

    for t_project in target_projects:
        eutils.update_data(projects, t_project, "lvariants", variants)

    if len(priority) == 1:
        projects.create_priority(priority, non_priority)

    return