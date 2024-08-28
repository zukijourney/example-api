import discord
from discord import app_commands
from discord.ext import commands
from ..utils import switcher

class SwitcherCog(commands.Cog):
    """
    Cog for property switching,
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="switch", description="Switches a property's status of an user.")
    @app_commands.describe(
        user="The user to switch the property of.",
        property="The property to switch.",
        status="The new status of the property."
    )
    @app_commands.choices(
        property=[
            app_commands.Choice(name="premium", value="premium_tier"),
            app_commands.Choice(name="banned", value="banned")
        ]
    )
    async def switch(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        status: str,
        property: app_commands.Choice[str]
    ) -> None:
        """Switches the property's status of an user."""
        await switcher(interaction, member=user, property=property.value, status=status)

async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(SwitcherCog(bot))