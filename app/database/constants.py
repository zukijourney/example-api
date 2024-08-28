import odmantic
import motor.motor_asyncio
from ..config import settings

engine = odmantic.AIOEngine(
    client=motor.motor_asyncio.AsyncIOMotorClient(settings.database_url),
    database=settings.database_name
)