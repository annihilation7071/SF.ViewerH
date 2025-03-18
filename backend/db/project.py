from backend.main_import import *
from .pool_variants import PoolVariant

log = logger.get_logger("Classes.db.project")

info_version = dep.DB_VERSION


class ProjectError(Exception):
    pass


class ProjectBase(SQLModel):
    lid: str = Field(..., unique=True, nullable=False)
    info_version: int = Field(default=info_version, index=True)
    lvariants: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    source_id: str = Field(default="unknown", index=True)
    source: str = Field(default="unknown", index=True)
    url: str = Field(default="unknown")
    downloader: str = Field(default="unknown", index=True)
    title: str = Field(default=None, index=True)
    subtitle: str | None = Field(default=None, index=True)
    upload_date: datetime | None = Field(default=None, index=True)
    preview: str = Field(default=None)
    parody: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    character: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    tag: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    artist: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    group: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    language: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    category: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    series: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    pages: int = Field(default=-1, sa_column=Column(JSON, index=True))
    episodes: list[str] = Field(default=[], sa_column=Column(JSON, index=True))
    preview_hash: str = Field(default="undefined", index=True)

    _path: Path | None = None

    class Config:
        validate_assignment = True
        allow_arbitrary_types = False

    @property
    def path(self) -> Path:
        log.debug("path")
        return self._path

    @property
    def preview_path(self) -> Path:
        log.debug("preview_path")
        return self.path / self.preview

    @classmethod
    def project_file_load(cls, file: Path):
        log.debug("project_file_load")
        data = utils.read_json(file)
        project = cls.model_validate(data)
        project._path = file.parent.parent
        return project

    def prolect_file_save(self, file: Path = None, fs: FSession = None):
        log.debug("project_file_save")
        if file is None:
            file = self.path / "sf.viewer/v_info.json"
        # exclude = {
        #     "id", "dir_name",
        #     "search_body", "active",
        #     "lib"
        # }
        # noinspection PyUnresolvedReferences
        include = set(ProjectBase.model_fields.keys())
        data = self.model_dump_json(include=include)
        file.parent.mkdir(parents=True, exist_ok=True)
        utils.write_json(file, json.loads(data), fs=fs)


class Project(ProjectBase, table=True):
    __tablename__ = "projects"

    id: int = Field(sa_column=Column("_id", Integer, primary_key=True))
    dir_name: str = Field(..., index=True)
    search_body: str = Field(default="undefined", index=True)
    active: bool = Field(default=True, index=True)
    lib: str = Field(..., index=True)

    # pool: str | None = Field(default=None, index=True)

    @property
    def _images_exts(self) -> set[str]:
        return {".png", ".jpg", ".jpeg", ".gif", ".avif", ".webp",
                ".bmp", ".tif", ".tiff", ".apng",
                ".mng", ".flif", ".bpg", ".jxl", ".qoi", ".hif"}

    @property
    def is_pool(self) -> bool:
        log.debug("is_pool")
        if self.lid.startswith("pool_"):
            log.debug("is_pool: True")
            return True
        log.debug("is_pool: False")
        return False

    @property
    def has_pool(self) -> str | None:
        log.debug("has_pool")
        with dep.Session() as session:
            pool_lid = session.scalar(
                select(PoolVariant.lid).where(
                    PoolVariant.project == self.lid
                )
            )

        return pool_lid

    @property
    def path(self) -> Path:
        log.debug("path")
        return Path(dep.libs[self.lib].path / self.dir_name)

    @property
    def path_info(self) -> Path:
        log.debug("path_info")
        return self.path / "sf.viewer/v_info.json"

    @property
    def upload_date_str(self) -> str:
        log.debug("upload_date_str")
        return self.upload_date.replace(microsecond=0).isoformat()

    @property
    def variants_view(self) -> list[str]:
        log.debug("variants_view")
        variants = [x.split(":") for x in self.variants]
        variants = [x[1] for x in variants]
        return variants

    @property
    def flags(self) -> list[Path]:
        log.debug("flags")
        exclude = ["rewrite", "translated"]

        flags_path = Path(os.getcwd()) / "data/flags"
        supports = os.listdir(flags_path)
        supports = [os.path.splitext(flag)[0] for flag in supports]

        flags = []

        for language in self.language:
            language = language.lower().strip()
            if language in supports:
                path = flags_path / f"{language}.svg"
                flags.append(path)
            else:
                if language not in exclude:
                    path = flags_path / "unknown.png"
                    flags.append(path)

        return flags

    @property
    def variants_count(self) -> int:
        log.debug("lvariants_count")
        return len(self.variants) - 1

    __cache_images__: list[dict[str, Path | int]] = None

    @property
    def images(self) -> list[dict[str, Path | int]]:
        log.debug("images")

        if self.__cache_images__ is not None:
            log.debug("images: using cache")
            return self.__cache_images__

        exts = self._images_exts
        files = os.listdir(self.path)
        pages = []

        for file in files:
            if os.path.splitext(file)[1].lower() in exts:
                pages.append(self.path / file)

        pages = sorted(pages, key=lambda x: str(x))
        pages = [{"idx": i, "path": pages[i]} for i in range(len(pages))]

        self.__cache_images__ = pages

        return pages

    __cache_variants__: list[PoolVariant] = None

    @property
    def variants(self) -> list[PoolVariant]:
        log.debug("variants")

        if self.__cache_variants__ is not None:
            log.debug("variants: using cache")
            return self.__cache_variants__

        with dep.Session() as session:
            if self.is_pool:
                lid = session.scalar(select(PoolVariant.project).where(
                    PoolVariant.lid == self.lid
                )
                )
            else:
                lid = self.lid

            log.debug(f"variants: lid: {lid}")

            stmt = select(PoolVariant).where(PoolVariant.project == lid)
            found = session.scalar(stmt)

            if not found:
                log.debug("variants: not found")
                return []

            log.debug("variants: found")

            variants = session.scalars(
                select(PoolVariant).where(
                    PoolVariant.lid == found.lid
                ).order_by(
                    desc(PoolVariant.priority),
                    asc(PoolVariant.description)
                )
            ).all()

            pool = PoolVariant(
                lid=variants[0].lid,
                project=variants[0].lid,
                description="pool",
                priority=False,
                update_time=datetime(2000, 1, 1),
            )

            variants = [pool] + list(variants)

            log.debug(f"variants: result: {variants}")

            self.__cache_variants__ = list(variants)

            return list(variants)

    @property
    def variants_edit_view(self) -> str:
        log.debug("variants_edit_view")

        result = []

        for variant in self.variants:
            lid = variant.project
            if lid.startswith("pool_"):
                continue
            # description = variant.description
            # priority = ":p" if variant.priority else ""
            # str_variant = f"{lid}:{description}{priority}"
            result.append(variant.to_str())

        result = "\n".join(result)
        return result

    @classmethod
    def project_file_load(cls, file: Path) -> None:
        log.debug("project_file_load")
        raise IOError("This method allowed only for ProjectBase class.")

    @classmethod
    def project_load_from_db(cls, session: Session, lid: str) -> 'Project':
        log.debug("project_load_from_db")
        stmt = select(Project).where(Project.lid == lid)
        project = session.scalar(stmt)
        return project

    def _project_renew_pages(self) -> bool:
        log.debug("project_renew_pages")
        exts = self._images_exts
        files = os.listdir(self.path)
        pages_count = len([file for file in files if os.path.splitext(file)[1].lower() in exts])
        if pages_count != self.pages:
            self.pages = pages_count
            return True
        return False

    def _project_renew_preview(self) -> bool:
        log.debug("_project_renew_preview")
        preview_name = ""

        files = os.listdir(self.path)

        for file in sorted(files):
            if os.path.splitext(file)[1].lower() in self._images_exts:
                preview_name = file
                break

        for file in files:
            if file.startswith(("preview", "_preview")):
                preview_name = file
                break

        if preview_name != self.preview:
            self.preview = preview_name
            self.preview_hash = utils.get_imagehash(self.preview_path)
            return True
        return False

    def _project_renew_search_body(self) -> bool:
        log.debug("_project_renew_search_body")
        search_body = utils.make_search_body(self)
        if self.search_body != search_body:
            self.search_body = search_body
            return True
        return False

    def project_renew_all(self) -> bool:
        log.debug("project_renew_all")
        return any([
            self._project_renew_search_body(),
            self._project_renew_pages(),
            self._project_renew_preview(),
        ])

    def project_db_update(self, session: Session) -> None:
        log.debug(f"project_db_update: {self.lid}")
        session.merge(self)

    def project_file_update(self, fs: FSession) -> None:
        log.debug(f"project_file_update: {self.lid}")
        if self.is_pool:
            raise ProjectError(f"Cannot update vinfo for pool: {self.lid}")

        file = self.path_info
        if file.exists():
            self.prolect_file_save(fs=fs)
        else:
            raise FileNotFoundError(f"File {file} not found")

    def project_update_project(self, session: Session, fs: FSession, renew: bool = False) -> None:
        log.debug(f"project_update_project: {self.lid}")
        if renew:
            self.project_renew_all()

        self.project_db_update(session=session)

        if self.is_pool:
            log.debug(f"Project {self.lid} is pool. Info file will not be updated.")
            return
        else:
            self.project_file_update(fs=fs)

    def project_add_to_db(self, session: Session) -> None:
        log.debug(f"project_add_to_db: {self.lid}")
        self.project_renew_all()
        session.add(self)

    def pool_sync_(self, session: Session) -> None:
        log.debug(f"pool_init_")
        if not self.is_pool:
            raise ProjectError(f"pool_init_: method allowed only for pool: {self.lid}")

        variants = self.variants[1:]
        log.debug(f"pool_init: variants: {variants}")
        projects_lids = [variant.project for variant in variants]

        projects = session.scalars(
            select(Project).where(
                Project.lid.in_(projects_lids),
            )
        ).all()

        log.debug(f"pool_init: projects: {projects}")

        synchronize_items = ["tag",
                             "artist", "group", "parody",
                             "character", "series", "language"]

        for item in synchronize_items:
            own = set(getattr(self, item))
            log.debug(f"pool_init: item: {item}, own: {own}")

            for project in projects:
                own = own | set(getattr(project, item))

            setattr(self, item, list(own))

            log.debug(f"pool_init: item: {item}, own: {own}")

