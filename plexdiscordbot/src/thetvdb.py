import os
import logging
import requests

baseurl = "https://api.thetvdb.com/"


def login():
    logging.info("Logging into TheTVDB...")
    url = f"{baseurl}login"
    payload = {"apikey": os.environ.get("PDB_THETVDB_KEY")}
    r = requests.post(url, json=payload)
    os.environ["PDB_THETVDB_TOKEN"] = r.json()["token"]


def get_series(thetvdb_id):
    url = f"{baseurl}series/{thetvdb_id}"
    headers = {"Authorization": f"Bearer {os.environ.get('PDB_THETVDB_TOKEN')}"}
    r = requests.get(url, headers=headers)
    return r.json()["data"]