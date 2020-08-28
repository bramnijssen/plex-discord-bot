from plexapi.server import PlexServer
import os

plex: PlexServer = PlexServer(os.environ.get("PDB_PLEX_BASEURL"), os.environ.get("PDB_PLEX_TOKEN"))


async def get_all_tv_shows():
    return plex.library.section(os.environ.get("PDB_PLEX_TV_SHOWS")).all()
