# Spotify Twitter Alert

## Twitter

https://twitter.com/SpotifyAlertFR

## Use Bot

- Create Database:

```
sqlite /var/SpotifyAlertFR/spotify.db
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
nano /etc/SpotifyAlertFR/SpotifyAlertFR.cfg
```

```
[SpotifyAlertFR]
twitter_consumer_key: xxx
twitter_consumer_secret: xx
twitter_access_token: xxx-xxx
twitter_access_token_secret: xxxx
spotify_client_id: xxxx
spotify_client_secret: xxxx
spotify_redirect_uri: https://xxxxx.wtf
```

- Set cron

```
crontab -e
```

```
2,12,22,32,42,52 * * * * cd /root/scripts/SpotifyAlertFR && /usr/bin/python3 /root/scripts/SpotifyAlertFR/SpotifyAlertFR.py >> /var/log/SpotifyAlertFR.log 2>&1
```

- Check live log

```
tail -f /var/log/daemon.log | grep SpotifyAlertFR
```

- Check old log

```
zgrep SpotifyAlertFR /var/log/daemon*
```


For the first run I advise you to comment `send_tweet(TWEET)` otherwise it will send a tweet for each old album. Think all the same to test that your credential twitter works correctly.
