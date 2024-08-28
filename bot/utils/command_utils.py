import discord
import typing
import time
import traceback
from ..config import settings
from ..database import UserManager

async def get_key(interaction: discord.Interaction) -> None:
    """Return an API key for an user."""
    try:
        await interaction.response.defer(ephemeral=True)
        
        user = await UserManager.get_user("user_id", interaction.user.id)

        if user:
            return await interaction.followup.send(f"Your API key is: {user.key}", ephemeral=True)
            
        new_user = await UserManager.create_user(interaction.user.id)

        await interaction.followup.send(f"Your new API key is: {new_user.key}", ephemeral=True)
    except (discord.HTTPException, discord.InteractionResponded):
        traceback.print_exc()
        return
    
async def reset_key_ip(interaction: discord.Interaction) -> None:
    """Reset the IP of an user's API key."""
    try:
        await interaction.response.defer(ephemeral=True)
        
        user = await UserManager.get_user("user_id", interaction.user.id)

        if not user:
            return await interaction.followup.send("You don't have an API key.", ephemeral=True)
        
        user.ip = None
        await UserManager.update_user("user_id", interaction.user.id, user.model_dump())

        await interaction.followup.send(f"Successfully reset the IP for {interaction.user.mention}.", ephemeral=True)
    except (discord.HTTPException, discord.InteractionResponded):
        traceback.print_exc()
        return

async def lookup(interaction: discord.Interaction, member: typing.Optional[discord.Member] = None) -> None:
    """Looks up an user."""
    try:
        await interaction.response.defer(ephemeral=True)

        if discord.utils.get(interaction.user.roles, name="bot-admin") is None and member:
            return await interaction.followup.send("You do not have permission to look up other users.", ephemeral=True)

        user = await UserManager.get_user("user_id", interaction.user.id if not member else member.id)

        if not user:
            return await interaction.followup.send("This user does not have an API key.", ephemeral=True)
        elif user.banned:
            return await interaction.followup.send("This user's API key has been banned.", ephemeral=True)
        
        await interaction.followup.send(f"Here is {interaction.user.mention if not member else member.mention}'s data: {user.model_dump_json()}", ephemeral=True)
    except (discord.HTTPException, discord.InteractionResponded):
        traceback.print_exc()
        return

async def switcher(interaction: discord.Interaction, member: discord.Member, property: str, status: str) -> None:
    """Switches the property's status of an user."""
    try:
        await interaction.response.defer(ephemeral=True)

        if discord.utils.get(interaction.user.roles, name="bot-admin") is None:
            return await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)

        user = await UserManager.get_user("user_id", interaction.user.id)

        if user is None:
            return await interaction.followup.send("This user does not have an API key.", ephemeral=True)
            
        if getattr(user, property) == status:
            return await interaction.followup.send(f"This user already has {property} with the status of {status}.", ephemeral=True)

        if property == "banned":
            await UserManager.update_user("user_id", member.id, {property: status == "true"})
        elif property == "premium_tier":
            user.premium_tier = int(status)

            if int(status) >= user.premium_tier:
                user.credits += 0 if int(status) == 0 else settings.credits[int(status) - 1]
                user.last_daily = time.time()

            await UserManager.update_user("user_id", member.id, user.model_dump())
        
        if property == "banned":
            if status:
                await interaction.followup.send(f"Successfully banned {member.mention}.", ephemeral=True)
            else:
                await interaction.followup.send(f"Successfully unbanned {member.mention}.", ephemeral=True)
        elif property == "premium_tier":
            if status:
                await interaction.followup.send(f"Successfully gave premium to {member.mention}.", ephemeral=True)
            else:
                await interaction.followup.send(f"Successfully removed the premium perks from {member.mention}.", ephemeral=True)
    except (discord.HTTPException, discord.InteractionResponded):
        traceback.print_exc()
        return