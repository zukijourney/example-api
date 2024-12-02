from discord import Interaction, Member, app_commands
from discord.ext import commands
from typing import Optional
from ..utils import Utils

class KeyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.utils = Utils()
    
    group = app_commands.Group(name='key', description='a')

    @group.command(name='get')
    async def get(self, interaction: Interaction) -> None:
        await self.utils.retrieve_api_key(interaction)

    @group.command(name='lookup')
    @app_commands.describe(user='[OPTIONAL] The user to lookup.')
    async def lookup(self, interaction: Interaction, user: Optional[Member] = None) -> None:
        await self.utils.user_lookup(interaction, user)
    
    @group.command(name='reset-ip')
    async def reset_ip(self, interaction: Interaction) -> None:
        await self.utils.reset_user_ip(interaction)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(KeyCog(bot))