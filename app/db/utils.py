import sqlmodel
from sqlalchemy.ext.asyncio import create_async_engine
from ..config import settings

engine = create_async_engine(settings.database_url, connect_args={"ssl": "disable"})

async def init_db():
    """Initialize the database."""
    async with engine.begin() as conn:
        await conn.run_sync(sqlmodel.SQLModel.metadata.create_all)