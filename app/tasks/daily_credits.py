import asyncio
import time
from ..config import settings
from ..database import User, engine

async def add_credits_daily() -> None:
    """
    Task for adding daily credits to users,
    with the amount being based on their premium tier.
    """

    while True:
        users = await engine.find(User, {})

        for user in users:
            if time.time() - user.last_daily >= 86400 and user.credits < 5000:
                user.credits += 22500 if user.premium_tier == 0 else settings.credits[user.premium_tier - 1]
                user.last_daily = time.time()

        await engine.save_all(users)

        await asyncio.sleep(300)