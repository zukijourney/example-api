import sqlmodel
import typing

class User(sqlmodel.SQLModel, table=True):
    """
    Represents the user table in the database.
    """    

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True)
    key: str = sqlmodel.Field(index=True)
    premium: bool = sqlmodel.Field(index=True)
    banned: bool = sqlmodel.Field(index=True)