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
        await db.init(self.bot)

        for guild in self.bot.guilds:
            logging.info(f"Joined {guild.name} as {self.bot.user}")

    @Cog.listener()
    async def on_member_join(self, member):
        db.insert_member(member)

    @Cog.listener()
    async def on_member_remove(self, member):
        db.delete_member(member)
