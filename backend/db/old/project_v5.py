from backend.main_import import *


class ProjectBaseV5(SQLModel):
    lid: str = Field(..., unique=True, nullable=False)
    info_version: int = Field(default=5, index=True)
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
        data = read_json(file)
        project = cls.model_validate(data)
        project._path = file.parent.parent
        return project

    def prolect_file_save(self, file: Path = None, fs: FSession = None):
        log.debug("project_file_save")
        if file is None:
            file = self.path / "sf.viewer/v_info.json"
        include = set(ProjectBase.model_fields.keys())
        data = self.model_dump_json(include=include)
        file.parent.mkdir(parents=True, exist_ok=True)
        write_json(file, json.loads(data), fs=fs)