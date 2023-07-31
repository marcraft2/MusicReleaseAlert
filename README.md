# Spotify Twitter Alert

## Twitter

https://twitter.com/SpotifyAlertFR
https://twitter.com/SpotifyAlertUS

## Use Bot

- Create Database:

```
sqlite /var/SpotifyAlert/spotify.db
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
mkdir /etc/SpotifyAlert
nano /etc/SpotifyAlert/SpotifyAlert.cfg
```

```
[SpotifyAlert]
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
database_file: /var/SpotifyAlert/spotify.db
```

- Set cron

```
crontab -e
```

```
2,12,22,32,42,52 * * * * cd /root/scripts/SpotifyAlert && /usr/bin/python3 /root/scripts/SpotifyAlert/SpotifyAlert.py >> /var/log/SpotifyAlert.log 2>&1
```

- Check live log

```
tail -f /var/log/daemon.log | grep SpotifyAlert
```

- Check old log

```
zgrep SpotifyAlert /var/log/daemon*
```
