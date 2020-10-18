from discord.ext.commands import Cog, Bot
import discord
import logging
import database as db
import plex
import datetime


def setup(bot):
    bot.add_cog(Events(bot))


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def process_alert(self, data):
        if data['type'] == 'timeline':

            # Item created
            if data['TimelineEntry'][0]['state'] == 0:

                # Episode level
                if data['TimelineEntry'][0]['type'] == 4:

                    # Get episode instance
                    episode_key = int(data['TimelineEntry'][0]['itemID'])
                    episode = plex.fetch_tv_show_item(episode_key)
                    
                    show_key = episode.grandparentRatingKey
                    subs = db.get_subscriptions_for_tv_show(show_key)

                    # If show has subscribers
                    if subs:

                        # Wait for metadata
                        stop = datetime.datetime.now() + datetime.timedelta(0, 10)
                        while episode.title == f"Episode {episode.index}" and datetime.datetime.now() < stop:
                            episode = plex.fetch_tv_show_item(episode_key)

                        # Extract info from episode
                        show_title = episode.grandparentTitle
                        season_number = episode.seasonNumber
                        episode_number = episode.index
                        episode_title = episode.title
                        summary = episode.summary

                        # Generate embed
                        embed = discord.Embed(
                            colour=discord.Colour.from_rgb(229, 160, 13),
                            title=f'Subscriptions - {show_title}',
                            description=f"A new episode of {show_title} has been added to the server!"
                        )
                        embed.add_field(name="Title", value=episode_title)
                        embed.add_field(name="Season", value=season_number)
                        embed.add_field(name="Episode", value=episode_number)

                        # If episode contains summary
                        if summary:
                            embed.add_field(name="Summary", value=summary, inline=False)

                        # Send message to subscribed users
                        for sub in subs:
                            user = await self.bot.fetch_user(sub['discord_id'])
                            await user.send(embed=embed)

    def plex_alert(self, data):               
        self.bot.loop.create_task(self.process_alert(data))

    @Cog.listener()
    async def on_ready(self):
        db.init()
        plex.start_alert_listener(self.plex_alert)

        for guild in self.bot.guilds:
            logging.info(f"Joined {guild.name} as {self.bot.user}")
