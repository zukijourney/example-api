import yaml
import time
import logging
from typing import Optional, Dict, Any
from discord import Interaction, Member, HTTPException, InteractionResponded, utils
from .db import UserManager

class Utils:
    def __init__(self):
        self._user_manager = UserManager()

        try:
            with open('credits.yml', 'r') as config_file:
                self._credits_config = yaml.safe_load(config_file)
        except FileNotFoundError:
            logging.error('Credits configuration file not found: credits.yml')
            self._credits_config = {}
        except yaml.YAMLError as e:
            logging.error(f'Error parsing credits configuration: {e}')
            self._credits_config = {}
    
    async def retrieve_api_key(self, interaction: Interaction) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
            
            user = await self._user_manager.get_user('user_id', interaction.user.id)

            if user:
                await interaction.followup.send(
                    f'Your existing API key is: {user["key"]}', 
                    ephemeral=True
                )
                return
            
            new_user = await self._user_manager.insert_user(interaction.user.id)

            await interaction.followup.send(
                f'Your new API key is: {new_user["key"]}', 
                ephemeral=True
            )
        
        except (HTTPException, InteractionResponded) as e:
            logging.error(f'Error retrieving API key: {e}')
            await interaction.followup.send(
                'An error occurred while processing your request.', 
                ephemeral=True
            )
    
    async def reset_user_ip(self, interaction: Interaction) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
            
            user = await self._user_manager.get_user('user_id', interaction.user.id)

            if not user:
                await interaction.followup.send(
                    'You do not have an existing API key.', 
                    ephemeral=True
                )
                return
            
            user['ip'] = None
            await self._user_manager.update_user('user_id', interaction.user.id, user)

            await interaction.followup.send(
                f'Successfully reset the IP for {interaction.user.mention}.', 
                ephemeral=True
            )
        
        except (HTTPException, InteractionResponded) as e:
            logging.error(f'Error resetting user IP: {e}')
            await interaction.followup.send(
                'An error occurred while resetting your IP.', 
                ephemeral=True
            )
    
    async def user_lookup(self, interaction: Interaction, member: Optional[Member] = None) -> None:
        try:
            await interaction.response.defer(ephemeral=True)

            is_admin = utils.get(interaction.user.roles, name='bot-admin') is not None
            target_user_id = member.id if member and is_admin else interaction.user.id

            if member and not is_admin:
                await interaction.followup.send(
                    'You do not have permission to look up other users.', 
                    ephemeral=True
                )
                return

            user = await self._user_manager.get_user('user_id', target_user_id)

            if not user:
                await interaction.followup.send(
                    'No API key found for this user.', 
                    ephemeral=True
                )
                return
            
            if user.get('banned', False):
                await interaction.followup.send(
                    'This user\'s API key has been banned.', 
                    ephemeral=True
                )
                return
            
            target_mention = member.mention if member else interaction.user.mention
            await interaction.followup.send(
                f'User data for {target_mention}: {user}', 
                ephemeral=True
            )
        
        except (HTTPException, InteractionResponded) as e:
            logging.error(f'Error during user lookup: {e}')
            await interaction.followup.send(
                'An error occurred during user lookup.', 
                ephemeral=True
            )
    
    async def modify_user_status(
        self, 
        interaction: Interaction, 
        member: Member, 
        property_name: str, 
        new_status: str
    ) -> None:
        try:
            await interaction.response.defer(ephemeral=True)

            if not utils.get(interaction.user.roles, name='bot-admin'):
                await interaction.followup.send(
                    'You do not have permission to modify user status.', 
                    ephemeral=True
                )
                return

            user = await self._user_manager.get_user('user_id', member.id)

            if not user:
                await interaction.followup.send(
                    'No API key found for this user.', 
                    ephemeral=True
                )
                return

            if property_name == 'banned':
                await self._handle_ban_modification(
                    interaction, member, user, new_status
                )
            elif property_name == 'premium_tier':
                await self._handle_premium_modification(
                    interaction, member, user, new_status
                )
            else:
                await interaction.followup.send(
                    f'Invalid property: {property_name}', 
                    ephemeral=True
                )
        
        except (HTTPException, InteractionResponded) as e:
            logging.error(f'Error modifying user status: {e}')
            await interaction.followup.send(
                'An error occurred while modifying user status.', 
                ephemeral=True
            )
    
    async def _handle_ban_modification(
        self, 
        interaction: Interaction, 
        member: Member, 
        new_status: str
    ) -> None:
        banned_status = new_status.lower() == 'true'
        await self._user_manager.update_user(
            'user_id', member.id, {'banned': banned_status}
        )
        
        status_message = (
            f'Successfully {"banned" if banned_status else "unbanned"} '
            f'{member.mention}.'
        )
        await interaction.followup.send(status_message, ephemeral=True)
    
    async def _handle_premium_modification(
        self, 
        interaction: Interaction, 
        member: Member, 
        user: Dict[str, Any], 
        new_status: str
    ) -> None:
        new_tier = int(new_status)
        user['premium_tier'] = new_tier

        if new_tier > 0:
            user['credits'] += self._credits_config.get(new_tier, 0)
            user['last_daily'] = time.time()

        await self._user_manager.update_user('user_id', member.id, user)
        
        status_message = (
            f'Successfully {"gave" if new_tier > 0 else "removed"} '
            f'premium to {member.mention}.'
        )
        await interaction.followup.send(status_message, ephemeral=True)