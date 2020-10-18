from plexapi.server import PlexServer
import os

plex: PlexServer = PlexServer(os.environ.get("PDB_PLEX_BASEURL"), os.environ.get("PDB_PLEX_TOKEN"))


def start_alert_listener(func):
    plex.startAlertListener(func)


def get_tv_shows_lib():
    return plex.library.section(os.environ.get("PDB_PLEX_TV_SHOWS"))


def get_all_tv_shows():
    return get_tv_shows_lib().all()


def fetch_tv_show_item(key):
    return get_tv_shows_lib().fetchItem(key)