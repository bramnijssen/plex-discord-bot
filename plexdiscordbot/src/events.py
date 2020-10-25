from discord.ext.commands import Cog, Bot
import discord
import logging
import database as db
import plex
import datetime
from os import getenv


def setup(bot):
    bot.add_cog(Events(bot))


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        db.init()
        plex.start_alert_listener(self.plex_alert)

        for guild in self.bot.guilds:
            logging.info(f"Joined {guild.name} as {self.bot.user}")

    @Cog.listener()
    async def on_member_remove(self, member):
        db.delete_subscriptions(member.id)

    async def process_alert(self, data):
        if data['type'] == 'timeline':

            # Item created
            if data['TimelineEntry'][0]['state'] == 0:

                # New show
                if data['TimelineEntry'][0]['type'] == 2:

                    # Get tv show instance
                    show_key = int(data['TimelineEntry'][0]['itemID'])
                    show = plex.fetch_tv_show_item(show_key)
                    show_title = show.title

                    db.add_tv_show(show_key, show_title)

                    channel_id = getenv('PDB_NEW_SHOW_CHANNEL_ID')

                    if channel_id:

                        # Wait for metadata
                        stop = datetime.datetime.now() + datetime.timedelta(0, 10)
                        while not show.summary and datetime.datetime.now() < stop:
                            show = plex.fetch_tv_show_item(show_key)

                        # Extract summary from show
                        summary = show.summary

                        # Generate embed
                        embed = discord.Embed(
                            colour=discord.Colour.from_rgb(229, 160, 13),
                            title=f'New Show - {show_title}',
                            description=f"{show_title} has been added to the server!"
                        )

                        # If episode contains summary
                        if summary:
                            embed.add_field(name="Summary", value=summary, inline=False)

                        channel = self.bot.get_channel(int(channel_id))
                        await channel.send(embed=embed)

                # New episode
                elif data['TimelineEntry'][0]['type'] == 4:

                    # Get episode instance
                    episode_key = int(data['TimelineEntry'][0]['itemID'])
                    episode = plex.fetch_tv_show_item(episode_key)
                    
                    show_key = episode.grandparentRatingKey
                    subs = db.get_subscriptions_from_plex_key(show_key)

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
                            user = self.bot.get_user(sub['discord_id'])
                            await user.send(embed=embed)

            # Item deleted
            elif data['TimelineEntry'][0]['state'] == 9:

                # Show deleted
                if data['TimelineEntry'][0]['type'] == 2:
                    show_key = int(data['TimelineEntry'][0]['itemID'])
                    subs = db.get_subscriptions_from_plex_key(show_key)

                    # If show has subscribers
                    if subs:
                        show_title = subs[0]['title']
                        tv_show_id = subs[0]['tv_show_id']

                        # Generate embed
                        embed = discord.Embed(
                            colour=discord.Colour.from_rgb(229, 160, 13),
                            title=f'Show Removed - {show_title}',
                            description=f"Your subscription for {show_title} has been removed since the show has been removed from the server."
                        )

                        # Send message to subscribed users and remove subscription
                        for sub in subs:
                            discord_id = sub['discord_id']

                            user = self.bot.get_user(discord_id)
                            db.unsubscribe(discord_id, tv_show_id)
                            await user.send(embed=embed)

                    # Delete show from database
                    db.delete_tv_show(show_key)


    def plex_alert(self, data):               
        self.bot.loop.create_task(self.process_alert(data))
