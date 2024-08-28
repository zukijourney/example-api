import os
import discord
from discord.ext import commands

class DiscordBot(commands.Bot):
    """
    The bot class for the Discord key bot.
    """
    
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=discord.Intents.default()
        )

    async def load_cogs(self) -> None:
        """Load all cogs before the bot starts."""
        for file in os.listdir(os.path.join(os.path.dirname(__file__), "cogs")):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(f"bot.cogs.{file[:-3]}")
                
    async def setup_hook(self) -> None:
        """Function executed before the bot starts for setting up the cogs."""
        await self.load_cogs()
        await self.tree.sync()
        print(f"Logged in as {self.user.global_name} (ID: {self.user.id})")