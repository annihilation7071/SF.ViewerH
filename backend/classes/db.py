from backend.main_import import *
from backend.utils import *
from backend import dep

log = logger.get_logger("Classes.db")


class ProjectBase(SQLModel):
    _info_path: Path | None = None
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

    @classmethod
    def project_file_load(cls, file: Path):
        data = utils.read_json(file)
        return cls.model_validate(data)

    def prolect_file_save(self, file: Path = None, fs: FSession = None):
        if file is None:
            file = self._info_path
        exclude = {
            "id", "dir_name",
            "search_body", "active",
            "lib"
        }
        data = self.model_dump_json(exclude=exclude)
        utils.write_json(file, json.loads(data), fs=fs)


class Project(ProjectBase, table=True):
    __tablename__ = "projects"
    id: int = Field(sa_column=Column("_id", Integer, primary_key=True))
    dir_name: str = Field(default=None, index=True)
    search_body: str = Field(default=None, index=True)
    active: bool = Field(default=True, index=True)
    lib: str = Field(default=None, index=True)

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

    @classmethod
    def project_file_load(cls, file: Path):
        raise IOError("This method allowed only for ProjectBase class.")







