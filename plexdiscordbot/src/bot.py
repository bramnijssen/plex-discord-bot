import logging
import discord
import asyncio
from discord.ext import commands
from os import getenv

if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    intents = discord.Intents.default()
    intents.members = True

    # Init bot and link to commands
    bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

    async def main():
        async with bot:
            await bot.load_extension("commands")
            await bot.load_extension("events")

            await bot.start(getenv("PDB_BOT_TOKEN"))

    asyncio.run(main())