import logging
import discord
from discord.ext import commands
import os

if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    intents = discord.Intents.default()
    intents.members = True

    # Init bot and link to commands
    bot = commands.Bot(command_prefix=".", intents=intents)

    bot.load_extension("commands")
    bot.load_extension("events")

    bot.run(os.environ.get("PDB_BOT_TOKEN"))
