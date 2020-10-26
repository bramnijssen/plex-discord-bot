from plexapi.exceptions import NotFound
from plexapi.server import PlexServer
from os import getenv

plex: PlexServer = PlexServer(getenv("PDB_PLEX_BASEURL"), getenv("PDB_PLEX_TOKEN"))


def start_alert_listener(func):
    plex.startAlertListener(func)


def get_tv_shows_lib():
    return plex.library.section(getenv("PDB_PLEX_TV_SHOWS"))


def get_all_tv_shows():
    return get_tv_shows_lib().all()


def fetch_tv_show_item(key):
    return get_tv_shows_lib().fetchItem(key)


def get_not_found_exception():
    return NotFound
