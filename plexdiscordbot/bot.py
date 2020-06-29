import discord
from plexapi.server import PlexServer
import os

client = discord.Client()
plex = PlexServer(os.environ.get("PDB_PLEX_BASEURL"), os.environ.get("PDB_PLEX_TOKEN"))

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))

client.run(os.environ.get("PDB_BOT_TOKEN"))
