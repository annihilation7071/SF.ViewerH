from backend.main_import import *
from backend.utils import *
from backend.filesession import FileSession, FSession
from backend import dep

log = logger.get_logger("Classes.db")


class ProjectError(Exception):
    pass


class ProjectBase(SQLModel):
    _path: Path | None = None
    lid: str = Field(..., unique=True, nullable=False)
    info_version: int = Field(..., index=True)
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

    class Config:
        validate_assignment = True
        allow_arbitrary_types = False

    @property
    def path(self) -> Path:
        return self._path

    @classmethod
    def project_file_load(cls, file: Path):
        data = utils.read_json(file)
        data["_path"] = file.parent.parent
        return cls.model_validate(data)

    def prolect_file_save(self, file: Path = None, fs: FSession = None):
        if file is None:
            file = self.path / "sf.viewer/v_info.json"
        exclude = {
            "id", "dir_name",
            "search_body", "active",
            "lib"
        }
        data = self.model_dump_json(exclude=exclude)
        file.parent.mkdir(parents=True, exist_ok=True)
        utils.write_json(file, json.loads(data), fs=fs)


class Project(ProjectBase, table=True):
    __tablename__ = "projects"

    id: int = Field(sa_column=Column("_id", Integer, primary_key=True))
    dir_name: str = Field(default=None, index=True)
    search_body: str = Field(default=None, index=True)
    active: bool = Field(default=True, index=True)
    lib: str = Field(default=None, index=True)

    _images_exts = {".png", ".jpg", ".jpeg", ".gif", ".avif", ".webp",
                    ".bmp", ".tif", ".tiff", ".apng",
                    ".mng", ".flif", ".bpg", ".jxl", ".qoi", ".hif"}

    @property
    def is_pool(self) -> bool:
        if self.lid.startswith("pool_"):
            return True
        return False

    @property
    def path(self) -> Path:
        return Path(dep.libs[self.lib] / self.dir_name)

    @property
    def preview_path(self) -> Path:
        return self.path / self.preview

    @property
    def upload_date_str(self) -> str:
        return self.upload_date.replace(microsecond=0).isoformat()

    @property
    def variants_view(self) -> list[str]:
        variants = [x.split(":") for x in self.lvariants]
        variants = [x[1] for x in variants]
        return variants

    @property
    def flags(self) -> list[Path]:
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
    def lvariants_count(self) -> int:
        return len(self.lvariants)

    @property
    def images(self) -> list[dict[str, Path | int]]:
        exts = self._images_exts
        files = os.listdir(self.path)
        pages = []

        for file in files:
            if os.path.splitext(file)[1].lower() in exts:
                pages.append(self.path / file)

        pages = sorted(pages, key=lambda x: str(x))
        pages = [{"idx": i, "path": pages[i]} for i in range(len(pages))]

        return pages

    @classmethod
    def project_file_load(cls, file: Path) -> None:
        raise IOError("This method allowed only for ProjectBase class.")

    @classmethod
    def project_load_from_db(cls, session: Session, lid: str) -> 'Project':
        stmt = select(Project).where(Project.lid == lid)
        project = session.scalar(stmt)
        return project

    def _project_renew_pages(self) -> bool:
        exts = self._images_exts
        files = os.listdir(self.path)
        pages_count = len([file for file in files if os.path.splitext(file)[1].lower() in exts])
        if pages_count != self.pages:
            self.pages = pages_count
            return True
        return False

    def _project_renew_preview(self) -> bool:
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
        log.debug(f"_update_search_body")
        search_body = utils.make_search_body(self)
        if self.search_body != search_body:
            self.search_body = search_body
            return True
        return False

    def project_renew_all(self) -> bool:
        return any([
            self.project_renew_search_body(),
            self._project_renew_pages(),
            self._project_renew_preview(),
        ])

    def project_db_update(self, session: Session) -> None:
        log.debug(f"_update_db: {self.lid}")
        session.merge(self)

    def project_file_update(self, fs: FSession) -> None:
        log.debug(f"_update_file: {self.lid}")
        if self.is_pool:
            raise ProjectError(f"Cannot update vinfo for pool: {self.lid}")

        file = self.path / "sf.viewer/v_info.json"
        if file.exists():
            self.prolect_file_save(fs=fs)
        else:
            raise FileNotFoundError(f"File {file} not found")

    def project_update_project(self, session: Session, fs: FSession, renew: bool = False) -> None:
        log.debug(f"_update_project: {self.lid}")
        if renew:
            self.project_renew_all()

        self.project_db_update(session=session)

        if self.is_pool:
            log.debug(f"Project {self.lid} is pool. Info file will not be updated.")
            return
        else:
            self.project_file_update(fs=fs)

    def project_add_to_db(self, session: Session) -> None:
        log.debug(f"_add_to_db: {self.lid}")
        session.add(self)

    def project_pool_create(self, session: Session) -> None:
        pool = Project








