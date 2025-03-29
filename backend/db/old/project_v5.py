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