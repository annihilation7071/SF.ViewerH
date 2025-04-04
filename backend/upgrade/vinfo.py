from backend.main_import import *

log = logger.get_logger("Upgrader")


class VInfoUpgrageError(Exception):
    pass


def upgrade(session: Session, project_path: Path, template_: ProjectBase = None) -> None | ProjectBase:
    log.debug("upgrade")
    if project_path:
        log.debug(project_path)
    if template_:
        log.debug(template_)

    vinfo_path = Path(project_path) / 'sf.viewer/v_info.json'
    upgraded = False

    if template_ is None:
        log.debug("Loading data into template from path.")
        template = ProjectBase.project_file_load(vinfo_path)
    else:
        template = template_

    if template.info_version == 2:
        log.debug("Current version is 2. Upgrading to 3.")
        template = upgrade_to_3(project_path, template)
        upgraded = True

    if template.info_version == 3:
        log.debug("Current version is 3. Upgrading to 4.")
        template = upgrade_to_4(template)
        upgraded = True

    if template.info_version == 4:
        log.debug("Current version is 4. Upgrading to 5.")
        template = upgrade_to_5(template, session)
        upgraded = True

    if template.info_version == 5:
        log.debug("Current version is 5. Upgrading to 6.")
        template = upgrade_to_6(template)
        upgraded = True

    if upgraded is False:
        log.debug("Upgrading not need.")
        if template_:
            log.debug("Returning template without changes.")
            return template
        return None

    if template_ is None:
        log.debug("Writing data into json file.")
        template.prolect_file_save()
    else:
        log.debug("Returning template.")
        return template


def upgrade_to_3(project_path: Path, template: ProjectBase) -> ProjectBase:
    log.debug("Upgrading to v3.")

    template.preview_hash = utils.get_imagehash(template.preview_path)
    log.debug(template.preview_hash)

    template.info_version = 3

    log.debug(f"Upgrade to version 3 completed")
    return template


def upgrade_to_4(template: ProjectBase) -> ProjectBase:
    log.debug("Upgrading to v4.")

    # Adding eposodes

    template.info_version = 4

    log.debug(f"Upgrade to version 4 completed")
    return template


def upgrade_to_5(template: ProjectBase, session: Session) -> ProjectBase:
    log.debug("Upgrading to v5.")

    # Adding eposodes
    template.info_version = 5

    def f(session_: Session):
        if len(template.lvariants) == 0:
            return

        pool_lid = f"pool_{utils.gen_lid()}"

        for variant in template.lvariants:
            # noinspection PyUnresolvedReferences
            variant: list = variant.split(":")
            if len(variant) == 2:
                variant += [False]
            else:
                variant[2] = True

            lid, description, priority = variant

            stmt = select(PoolVariant).where(PoolVariant.project == lid)
            found = session.scalar(stmt)

            if found:
                return

            pool_entry = PoolVariant(
                lid=pool_lid,
                project=lid,
                description=description,
                priority=priority,
                update_time=datetime.now(),
            )

            session.add(pool_entry)

    if session is None:
        with dep.Session() as session:
            f(session)
            session.commit()
    else:
        f(session)

    template.lvariants = ["depricated"]

    log.debug(f"Upgrade to version 5 completed")
    return template


def upgrade_to_6(template: ProjectBase) -> ProjectBase:
    log.debug("Upgrading to v6.")

    # Adding eposodes

    template.info_version = 6

    log.debug(f"Upgrade to version 6 completed")
    return template