from backend.main_import import *


log = logger.get_logger("Classes.db.pool")


class PoolVariantError(Exception):
    pass


class PoolVariantBase(SQLModel):
    lid: str = Field(..., index=True)
    project: str = Field(..., index=True, unique=True)
    description: str = Field(..., index=True)
    priority: bool = Field(default=False, index=True)
    update_time: datetime = Field(..., index=True)

    class Config:
        validate_assignment = True
        allow_arbitrary_types = False


class PoolVariant(PoolVariantBase, table=True):
    __tablename__ = "pools_variants"

    id: int = Field(..., index=True, primary_key=True)

    __table_args__ = (
        Index(
            "unique_priority_for_every_pool",
            "lid",
            unique=True,
            sqlite_where=column("priority") == 1,
        ),
    )


