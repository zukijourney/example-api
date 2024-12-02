from .config import settings
from .main import DiscordBot

bot = DiscordBot()
bot.run(settings.token)