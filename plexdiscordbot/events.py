from discord.ext.commands import Cog, Bot
import logging
import database as db


def setup(bot):
    bot.add_cog(Events(bot))


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            logging.info(f"Joined {guild.name} as {self.bot.user}")

        await db.init()
