"""
Spotify Twitter Bot - SpotifyAlertFR
"""

from requests_oauthlib import OAuth1Session
from logging.handlers import SysLogHandler
from datetime import datetime, timedelta
from spotipy.oauth2 import SpotifyOAuth
from configparser import ConfigParser
from twitter_text import parse_tweet
import sqlite3
import logging
import spotipy
import tweepy
import json
import os

from artistes import ARTISTES

# Configuration
DEFAULT_CONFIG = {
    "SpotifyAlertFR": {
        "twitter_consumer_key": "YOUR TWITTER consumer_key",
        "twitter_consumer_secret": "YOUR TWITTER consumer_secret",
        "twitter_access_token": "YOUR TWITTER access_token",
        "twitter_access_token_secret": "YOUR TWITTER access_token_secret",
        "spotify_client_id": "YOUR SPOTIFY client_id",
        "spotify_client_secret": "YOUR SPOTIFY client_secret",
        "spotify_redirect_uri": "YOUR SPOTIFY redirect_uri",
        "log_level": "info",
        "log_address": "/dev/log",
        "log_facility": "daemon",
        "database_file": '/var/SpotifyAlertFR/spotify.db'
    }
}

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
        msg = "Nouvelle album ajoutée avec succès a la DB! {} - {} album_id: {}"
        logger.info(msg.format(artist_name, album_name, album_id))
    except sqlite3.Error as e:
        conn.rollback()
        logger.info("Erreur lors de l'ajout de la release :", e)
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
        logger.info("Erreur lors de la vérification de l'artiste :", e)
        conn.close()
        return False


def send_tweet(text):
    payload = {"text": text}
    oauth = OAuth1Session(
        client_key=config["twitter_consumer_key"],
        client_secret=config["twitter_consumer_secret"],
        resource_owner_key=config["twitter_access_token"],
        resource_owner_secret=config["twitter_access_token_secret"],
    )
    # Acces token generer sur le compte de AlertSpotify
    # https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Manage-Tweets/create_tweet.py
    # Valider le code avec le compte en question

    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        msg = "Request returned an error: {} {}" \
                                  .format(response.status_code, response.text)
        logger.info(msg)
        raise Exception(msg)

    json_response = response.json()
    str_ = json.dumps(json_response, indent=4, sort_keys=True)
    data = json.loads(str_)
    logger.info("New Tweet -> https://twitter.com/SpotifyAlertFR/status/{}" \
                                                    .format(data['data']['id']))

def convert_duration(duration_ms):
    duration_sec = duration_ms // 1000
    hours = duration_sec // 3600
    minutes = (duration_sec % 3600) // 60
    seconds = duration_sec % 60
    if hours > 0:
        formatted_duration = f"{hours}h{minutes:02}m{seconds:02}s"
    elif minutes > 0:
        formatted_duration = f"{minutes}m{seconds:02}s"
    else:
        formatted_duration = f"{seconds}s"
    return formatted_duration

def is_date_less_than_2_days_ago(date_string):
    date_format = "%Y-%m-%d"
    given_date = datetime.strptime(date_string, date_format)
    current_date = datetime.now()
    difference = current_date - given_date
    if difference < timedelta(days=3):
        return True
    else:
        return False

def check_for_artiste(artist_id, twitter, limit=20):
    sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(client_id=config["spotify_client_id"],
                                  client_secret=config["spotify_client_secret"],
                                    redirect_uri=config["spotify_redirect_uri"],
                                                     scope='user-library-read'))

    r = sp.artist(artist_id)
    artist_name = r['name']

    albums = sp.artist_albums(artist_id, limit=limit)
    latest_releases = sorted(albums['items'],
                             key=lambda k: k['release_date'],
                             reverse=True)
    for release in latest_releases:
        if not album_exist(release['id']):

            r = sp.album_tracks(release['id'])

            for i in r['items']:
                if i['artists'][0]['id'] !== artist_id:
                    break
            else:
                logger.info("L'artiste n'est pas celui rechercher {} {}"  \
                                     .format(i['artists'][0]['id'], artist_id))
                continue

            if release['album_type'] == 'single':
                if len(r['items']) == 1:
                    album_type = release['album_type']
                else:
                    album_type = 'EP'
            else:
                album_type = release['album_type']

            if twitter == 'not found':
                TWEET = "Nouveau {} de {}\n\n{} - {}\n\nTrack:\n" \
                                                .format(album_type,
                                                        artist_name,
                                                        release['name'],
                                                        release['release_date'])
            else:
                TWEET = "Nouveau {} de {} ({})\n\n{} - {}\n\nTrack:\n" \
                                                .format(album_type,
                                                        artist_name,
                                                        twitter,
                                                        release['name'],
                                                        release['release_date'])

            failed_line = False
            for item in r['items']:
                artites_lists = []

                for art in item['artists']:
                    if art['id'] == artist_id:
                        continue
                    name_ = art['name']
                    for artiste in ARTISTES:
                        if art['id'] == artiste['spotify_id'] \
                        and artiste['twitter_tag'] !== 'not found':
                            name_ = artiste['twitter_tag']
                    artites_lists.append(name_)

                r_track = sp.track(item['id'])
                if len(artites_lists):
                    new_line = " • {} (feat {}) - {}\n".format(item['name'],
                                                   ', '.join(artites_lists),
                                   convert_duration(r_track['duration_ms']))
                else:
                    new_line = " • {} - {}\n".format(item['name'],
                         convert_duration(r_track['duration_ms']))

                if parse_tweet(TWEET+new_line).asdict()['weightedLength'] < 250:
                    TWEET = TWEET + new_line
                else:
                    failed_line = True

            if failed_line:
                TWEET = TWEET + '[...]\n'

            TWEET = TWEET + release['external_urls']['spotify']

            if is_date_less_than_2_days_ago(release['release_date']):
                send_tweet(TWEET)
            else:
                logger.info('Ancien Album {} - {} {} {}'.format(artist_name,
                                                                release['name'],
                                                                release['id'],
                                                       release['release_date']))

            add_album(artist_id, artist_name, release['id'],
                                     release['name'], release['release_date'],
                                     release['album_type'])

        else:
            msg = 'Album already exist on DB {}: {} - {}'
            logger.debug(msg.format(release['id'], artist_name,
                                                  release['release_date']))


if __name__ == "__main__":
    # Load configuration
    n = 'SpotifyAlertFR'
    cp = ConfigParser()
    cp.read_dict(DEFAULT_CONFIG)
    cp.read(f'/etc/{n}/{n}.cfg')
    config = cp[n]

    # Setup syslog logger
    log_level = logging.getLevelName(config["log_level"].upper())
    logger = logging.getLogger(n)
    logger.setLevel(log_level)
    slog = SysLogHandler(config["log_address"], config["log_facility"])
    slog.setLevel(log_level)
    slog.setFormatter(logging.Formatter("SpotifyAlertFR: {message}", style="{"))
    logger.addHandler(slog)
    logger.info(f"{n} started")

    for artiste in ARTISTES:
        check_for_artiste(artiste['spotify_id'], artiste['twitter_tag'])

    logger.info(f"{n} ended")
