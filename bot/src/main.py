import os
import discord
from discord.ext import commands

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=discord.Intents.default()
        )

    async def load_cogs(self) -> None:
        for file in os.listdir(os.path.join(os.path.dirname(__file__), 'cogs')):
            if file.endswith('.py') and not file.startswith('_'):
                await self.load_extension(f'src.cogs.{file[:-3]}')
                
    async def setup_hook(self) -> None:
        await self.load_cogs()
        await self.tree.sync()
        print(f'Logged in as {self.user} (ID: {self.user.id})')