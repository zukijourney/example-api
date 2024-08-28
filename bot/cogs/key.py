import discord
import typing
from discord import app_commands
from discord.ext import commands
from ..utils import get_key, lookup, reset_key_ip

class KeyCog(commands.Cog):
    """
    Cog for key management.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    group = app_commands.Group(name="key", description="Commands for managing your API key.")

    @group.command(name="get", description="Returns your API key.")
    async def get(self, interaction: discord.Interaction) -> None:
        """Generates an API key."""
        await get_key(interaction)
    
    @group.command(name="lookup", description="Looks up a user's API key.")
    @app_commands.describe(user="[OPTIONAL] The user to lookup.")
    async def lookup(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None) -> None:
        """Looks up a user's API key."""
        await lookup(interaction, user)
    
    @group.command(name="reset-ip", description="Resets your API key.")
    async def reset_ip(self, interaction: discord.Interaction) -> None:
        """Looks up a user's API key."""
        await reset_key_ip(interaction)

async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(KeyCog(bot))