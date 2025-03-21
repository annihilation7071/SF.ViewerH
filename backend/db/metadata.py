from backend.main_import import *

log = logger.get_logger("DB.metadata")


class DBMetadataError(Exception):
    pass


class DBMetadata(SQLModel, table=True):
    __tablename__ = "metadata"

    id: int = Field(..., index=True, primary_key=True)
    variants_updated: datetime = Field(default=datetime(2000, 1, 1), index=True, nullable=False)

    # __table_args__ = (
    #     Index(
    #         "only_one_item",
    #         "id",
    #         unique=True,
    #         sqlite_where=column("id") > 0,
    #     ),
    # )

    @classmethod
    def load(cls, session: Session) -> 'DBMetadata':

        result = session.scalar(select(DBMetadata))
        if not result:
            result = DBMetadata()
            session.add(result)

        return result



