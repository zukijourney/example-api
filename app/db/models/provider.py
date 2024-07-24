import sqlmodel
import sqlalchemy
import typing
from sqlalchemy.dialects.postgresql import ARRAY

class Provider(sqlmodel.SQLModel, table=True):
    """
    Represents the provider table in the database.
    """

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True)
    api_key: str = sqlmodel.Field(index=True)
    api_url: str = sqlmodel.Field(index=True)
    models: typing.List[str] = sqlmodel.Field(sa_column=sqlalchemy.Column(ARRAY(sqlalchemy.String)))
    usage: int = sqlmodel.Field(index=True)
    failures: int = sqlmodel.Field(index=True)