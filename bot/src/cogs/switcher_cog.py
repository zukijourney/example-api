import discord
from discord import app_commands
from discord.ext import commands
from ..utils import Utils

class SwitcherCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.utils = Utils()

    @app_commands.command(name='switch')
    @app_commands.describe(
        user='The user to switch the property of.',
        property='The property to switch.',
        status='The new status of the property.'
    )
    @app_commands.choices(
        property=[
            app_commands.Choice(name='premium', value='premium_tier'),
            app_commands.Choice(name='banned', value='banned')
        ]
    )
    async def switch(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        status: str,
        property: app_commands.Choice[str]
    ) -> None:
        await self.utils.modify_user_status(
            interaction,
            user,
            property.value,
            status
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SwitcherCog(bot))