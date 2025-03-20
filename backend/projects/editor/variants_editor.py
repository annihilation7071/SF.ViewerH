from backend.main_import import *

log = logger.get_logger("Projects.editor.variants_editor")

if TYPE_CHECKING:
    from backend.projects.projects import Projects


class VariantsEditorError(Exception):
    pass


def edit(session: Session, fs: FSession, project: Project, data: str) -> str | None:
    log.debug(f"variant_editor")
    log.debug(f"variant_editor: data: {data}")

    new_variants = data.split("\n")
    new_variants = [variant.strip() for variant in new_variants if variant != ""]
    log.debug(f"variant_editor: new_variants: {new_variants}")

    if len(new_variants) == 0:
        if project.has_pool is False:
            log.debug(f"project has no pool: {project.lid}")
            return project.lid
        pool_lid = project.get_pool_lid()
        dep.projects.delete_pool_(session, pool_lid)
        log.debug(f"variant_editor: pool deleted {pool_lid}")
        return None

    validator = r'^([a-zA-Z0-9]+_[a-zA-Z0-9]+:([^:^\n]+))(:(PRIORITY|priority|p|P))?$'
    for variant in new_variants:
        match = re.fullmatch(validator, variant)
        if not match:
            raise VariantsEditorError(f"Incorrect input data: {variant}: {new_variants}")

    new_variants = [PoolVariantBase.from_str(string) for string in new_variants]

    priority = first_true(new_variants, lambda variant: variant.priority)

    if not priority:
        raise VariantsEditorError(f"Incorrect input data: {new_variants}")

    if project.has_pool:
        if priority.project == project.variants[1].project:
            lid = project.get_pool_lid()
            log.debug(f"variant_editor: priority project already has pool, using this lid: {lid}")
        else:
            lid = f"pool_{utils.gen_lid()}"
            log.debug(f"variant_editor: creating new pool {lid}")

        pool_lid = project.get_pool_lid()
        dep.projects.delete_pool_(session, pool_lid)

    else:
        lid = f"pool_{utils.gen_lid()}"
        log.debug(f"variant_editor: creating new pool {lid}")

    log.debug(f"variant_editor: pool lid: {lid}")

    new_variants = [PoolVariant(
        lid=lid,
        **variant.model_dump()
    ) for variant in new_variants]

    session.add_all(new_variants)

    dep.projects.update_pools_(session)
    log.debug(f"variant_editor: completed")
    return lid











