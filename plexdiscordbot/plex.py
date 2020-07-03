from plexapi.server import PlexServer
import os

plex: PlexServer


async def init():
    # Bind server connection to var
    global plex
    plex = PlexServer(os.environ.get("PDB_PLEX_BASEURL"), os.environ.get("PDB_PLEX_TOKEN"))


async def get_all_tv_shows():
    return plex.library.section(os.environ.get("PDB_PLEX_TV_SHOWS")).all()
