from backend.main_import import *

log = logger.get_logger("DB.pool_variants")


class PoolVariantError(Exception):
    pass


class PoolVariantBase(SQLModel):
    project: str = Field(..., index=True, unique=True)
    description: str = Field(..., index=True)
    priority: bool = Field(default=False, index=True)
    update_time: datetime = Field(..., index=True)

    class Config:
        validate_assignment = True
        allow_arbitrary_types = False

    def to_str(self) -> str:
        log.debug("to_str")
        result = f"{self.project}:{self.description}"
        if self.priority:
            result += ":p"
        return result

    @classmethod
    def from_str(cls, string: str) -> Union["PoolVariantBase", "PoolVariant"]:
        log.debug("from_str")
        separated = string.split(":")

        if len(separated) > 3 or len(separated) < 2:
            raise PoolVariantError(f"from_str: incorrect format: {string}")

        project_lid = separated[0]
        description = separated[1]

        if len(separated) == 3 and separated[2].lower() in ["p", "priority"]:
            priority = True
        else:
            priority = False

        result = cls(
            project=project_lid,
            description=description,
            priority=priority,
            update_time=datetime.now(),
        )

        return result


class PoolVariant(PoolVariantBase, table=True):
    __tablename__ = "pools_variants"

    id: int = Field(..., index=True, primary_key=True)
    lid: str = Field(..., index=True)

    __table_args__ = (
        Index(
            "unique_priority_for_every_pool",
            "lid",
            unique=True,
            sqlite_where=column("priority") == 1,
        ),
    )

    # @property
    # def active(self) -> bool:
    #     pass
