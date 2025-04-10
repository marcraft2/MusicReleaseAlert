"""
Spotify Telegram Bot - MusicReleaseAlert
"""

from configparser import ConfigParser
from datetime import datetime
from datetime import timedelta
import json
import logging
from logging.handlers import SysLogHandler
import sqlite3
import sys
import urllib

from musicreleasealert.artists import ARTISTS
from requests_oauthlib import OAuth1Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
from telegram import Bot

# Configuration
DEFAULT_CONFIG = {
    "MusicReleaseAlert": {
        "telegram_token": "XXX",
        "spotify_client_id": "YOUR SPOTIFY client_id",
        "spotify_client_secret": "YOUR SPOTIFY client_secret",
        "spotify_redirect_uri": "YOUR SPOTIFY redirect_uri",
        "log_level": "info",
        "log_address": "/dev/log",
        "log_facility": "daemon",
        "database_file": "/var/MusicReleaseAlert/spotify.db",
    }
}

n = "MusicReleaseAlert"
cp = ConfigParser()
cp.read_dict(DEFAULT_CONFIG)
cp.read(f"/etc/{n}/{n}.cfg")
config = cp[n]

log_level = logging.getLevelName(config["log_level"].upper())
logger = logging.getLogger(n)
logger.setLevel(log_level)

slog = SysLogHandler(config["log_address"], config["log_facility"])
# slog = logging.StreamHandler()

slog.setLevel(log_level)
slog.setFormatter(logging.Formatter("MusicReleaseAlert: {message}", style="{"))
logger.addHandler(slog)


def add_album(artist_id, artist_name, album_id, album_name, album_d, album_t):
    conn = sqlite3.connect(config["database_file"])
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO last_release (artist_id, artist_name, album_id,
                              album_name, album_date, album_type)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    data = (artist_id, artist_name, album_id, album_name, album_d, album_t)
    try:
        cursor.execute(insert_query, data)
        conn.commit()
        msg = "New release successfully added to the DB! {} - {} album_id: {}"
        logger.info(msg.format(artist_name, album_name, album_id))
    except sqlite3.Error as e:
        conn.rollback()
        logger.info("Error while adding the release:", e)
    finally:
        conn.close()


def album_exist(album_id):
    conn = sqlite3.connect(config["database_file"])
    cursor = conn.cursor()
    select_query = "SELECT COUNT(*) FROM last_release WHERE album_id = ?"
    data = (album_id,)
    try:
        cursor.execute(select_query, data)
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0
    except sqlite3.Error as e:
        logger.info("Error verifying artist:", e)
        conn.close()
        return False


def convert_duration(duration_ms):
    duration_sec = duration_ms // 1000
    hours = duration_sec // 3600
    minutes = (duration_sec % 3600) // 60
    seconds = duration_sec % 60
    if hours > 0:
        formatted_duration = f"{hours}h{minutes}m{seconds}s"
    elif minutes > 0:
        formatted_duration = f"{minutes}m{seconds}s"
    else:
        formatted_duration = f"{seconds}s"
    return formatted_duration


def is_date_less_than_2_days_ago(date_string):
    if len(date_string) == 4:
        date_format = "%Y"
    else:
        date_format = "%Y-%m-%d"
    given_date = datetime.strptime(date_string, date_format)
    current_date = datetime.now()
    difference = current_date - given_date
    if difference < timedelta(days=3):
        return True
    else:
        return False

def cleanup_str(s):
    return s.replace('_', '\_') \
          .replace('*', '\*') \
          .replace('[', '\[') \
          .replace(']', '\]') \
          .replace('(', '\(') \
          .replace(')', '\)') \
          .replace('~', '\~') \
          .replace('`', '\`') \
          .replace('>', '\>') \
          .replace('#', '\#') \
          .replace('+', '\+') \
          .replace('-', '\-') \
          .replace('=', '\=') \
          .replace('|', '\|') \
          .replace('{', '\{') \
          .replace('}', '\}') \
          .replace('.', '\.') \
          .replace('!', '\!')


def send_telegram_message(msg="Hello World", chat_id='-4214946076'):
    bot = Bot(token=config['telegram_token'])
    async def send_message():
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode='MarkdownV2')
    asyncio.run(send_message())


def check_for_artiste(artist_id, lang):
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config["spotify_client_id"],
            client_secret=config["spotify_client_secret"],
            redirect_uri=config["spotify_redirect_uri"],
            scope="user-library-read",
        )
    )

    r = sp.artist(artist_id)

    artist_name = f"[{r['name']}](https://open.spotify.com/artist/{artist_id})"

    albums = sp.artist_albums(artist_id, limit=20)
    latest_releases = sorted(
        albums["items"], key=lambda k: k["release_date"], reverse=True
    )
    for release in latest_releases:
        if not album_exist(release["id"]):
            if (
                release["album_type"] == "appears_on"
                or release["artists"][0]["id"] != artist_id
            ):
                logger.debug(
                    "Bad Artists {} album_id: {}".format(artist_id, release["id"])
                )
                continue

            r = sp.album_tracks(release["id"])

            if release["album_type"] == "single":
                if len(r["items"]) == 1:
                    album_type = release["album_type"]
                else:
                    album_type = "EP"
            else:
                album_type = release["album_type"]

            _MSG = "New {} by {}\n\n[{}]({}) \- {}\n\nTrack:\n".format(
                album_type, artist_name, cleanup_str(release["name"]), release["external_urls"]["spotify"], cleanup_str(release["release_date"])
            )


            for item in r["items"]:
                artites_lists = []

                for art in item["artists"]:
                    if art["id"] == artist_id:
                        continue

                    artites_lists.append(art['name'])

                r_track = sp.track(item["id"])
                if len(artites_lists):
                    track_name = item["name"]
                    if "(feat" in track_name:
                        try:
                            track_name = (
                                track_name.split("(", 1)[0].strip()
                                + " "
                                + track_name.split(")", 1)[1].strip()
                            )
                        except Exception as e:
                            logger.info(f'ERROR: Fail to edit feat: {track_name} => {e}')
                            pass

                    new_line = " • {} \(feat {}\) \- {}\n".format(
                        cleanup_str(track_name),
                        cleanup_str(", ".join(artites_lists)),
                        convert_duration(r_track["duration_ms"]),
                    )
                else:
                    new_line = " • {} \- {}\n".format(
                        cleanup_str(item["name"]), convert_duration(r_track["duration_ms"])
                    )

                _MSG = _MSG + new_line

            if is_date_less_than_2_days_ago(release["release_date"]):
                try:
                    send_telegram_message(_MSG)
                except Exception as e:
                    print(_MSG)
                    sys.exit(1)

            else:
                logger.info(
                    "Old Release {} - {} {} {}".format(
                        artist_name,
                        release["name"],
                        release["id"],
                        release["release_date"],
                    )
                )

            add_album(
                artist_id,
                artist_name,
                release["id"],
                release["name"],
                release["release_date"],
                release["album_type"],
            )

        else:
            msg = "Album already exist on DB {}: {} - {}"
            logger.debug(
                msg.format(release["id"], artist_name, release["release_date"])
            )


def main():
    logger.info(f"{n} started")
    
    for lang in ["fr", "us"]:
        for artiste in ARTISTS[lang]:
            check_for_artiste(artiste["spotify_id"], lang)

    logger.info(f"{n} ended")


if __name__ == "__main__":
    main()
