from discord.ext.commands import Bot
import bot.models
from bot.config import config

client = Bot(command_prefix=config["BOT_PREFIX"], case_insensitive=True)
chat_bot = bot.models.ChatBot(config["MINIMUM_CONFIDENCE"], config["MAXIMUM_CONFIDENCE"])

from bot import events, commands
