# Music Release Twitter Alert

## Twitter

- https://twitter.com/MusicReleaseAlertFR
- https://twitter.com/MusicReleaseAlertUS

## Use Bot

- Create Database:

```
sqlite /var/MusicReleaseAlert/releases.db
```

```
CREATE TABLE IF NOT EXISTS last_release (
    album_id VARCHAR(256) PRIMARY KEY,
    artist_id VARCHAR(256),
    artist_name VARCHAR(256),
    album_name VARCHAR(256),
    album_date VARCHAR(256),
    album_type VARCHAR(256),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```


- Set Configuration

```
mkdir /etc/MusicReleaseAlert
nano /etc/MusicReleaseAlert/MusicReleaseAlert.cfg
```

```
[MusicReleaseAlert]
fr_twitter_consumer_key: xxx
fr_twitter_consumer_secret: xx
fr_twitter_access_token: xxx-xxx
fr_twitter_access_token_secret: xxxx
us_twitter_consumer_key: xxx
us_twitter_consumer_secret: xx
us_twitter_access_token: xxx-xxx
us_twitter_access_token_secret: xxxx
spotify_client_id: xxxx
spotify_client_secret: xxxx
spotify_redirect_uri: https://xxxxx.wtf
database_file: /var/MusicReleaseAlert/spotify.db
```

- Set cron

```
crontab -e
```

```
2,12,22,32,42,52 * * * * cd /usr/local/MusicReleaseAlert && /usr/bin/poetry run MusicReleaseAlert >> /var/log/MusicReleaseAlert.log 2>&1
```
