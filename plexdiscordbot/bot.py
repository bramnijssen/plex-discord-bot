import logging
import database
from discord.ext import commands
import os
import asyncio

if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    # Init bot and link to commands
    bot = commands.Bot(command_prefix=".")

    bot.load_extension("commands")
    bot.load_extension("events")

    bot.run(os.environ.get("PDB_BOT_TOKEN"))
