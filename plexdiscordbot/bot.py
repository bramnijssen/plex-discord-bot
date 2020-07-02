import logging
import database
from discord.ext import commands
import os
import asyncio


async def init():
    await database.init()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())

    bot = commands.Bot(command_prefix=".")
    bot.run(os.environ.get("PDB_BOT_TOKEN"))
