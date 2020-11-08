# PlexDiscordBot
Discord bot which notifies server members about Plex events. The bot is written in Python and designed to be run via Docker.

## Features
* Server members can (un)subscribe to TV Shows available on the connected Plex server.
* Upon adding an episode of a show to the Plex server, server members who are subscribed to the show will get notified about the new episode via a DM with some additional information about the episode.
* Option to specify a channel in the server in which a message will be posted when a new show has been added to the Plex server. This message will also include some additional information about the show.

## Requirements
Make sure you have:
* Installed [Docker](https://docs.docker.com/get-docker/)
* Installed [Docker Compose](https://docs.docker.com/compose/install/)
* Created a Discord bot and retrieved its token. See [this guide](https://discordpy.readthedocs.io/en/latest/discord.html) for instructions. **Make sure to set the correct [permissions](#discord-bot-requirements).**

## Discord bot requirements
Server Members Intent has to be turned on (located in Privileged Gateway Intents). And the Permission Integer has to be set to 10304 (= Send Messages, Manage Messages, Add Reactions).

## Setup
1. Clone the repository
1. Provide info in the .env.example file
    * PDB_BOT_TOKEN: Token of the created bot.
    * PDB_NEW_SHOW_CHANNEL_ID: Channel ID of the channel in the server in which messages will be sent when a new show has been added to the Plex server. See [this guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) on how to retrieve a channel's ID. If you do not wish to use this feature, then remove the entire line containing the variable from the file.
    * PDB_PLEX_BASEURL: The IP or URL of the Plex server (e.g. http://localhost:32400/).
    * PDB_PLEX_TOKEN: Token to access Plex. See [this guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) on how to retrieve the token.
    * PDB_PLEX_TV_SHOWS: The name of the TV shows library. Plex's default is "TV Shows" (without quotes).
1. Rename .env.example to .env
1. Start the bot with `docker-compose up -d`

## Commands
* `.help`: Shows the help message with the list of available commands.
* `.sub | .subscribe <search_term>`: Search for a TV show to which you want to subscribe / unsubscribe. When subscribed to a TV show, you will receive a notification when a new episode of that TV show has been added to the server.
* `.shows | .tvshows`: Lists available TV Shows.
* `.subs | .subscriptions`: Lists subscriptions.