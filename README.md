# Music Release Telegram Alert

## Use Bot

- Install Poetry

```
curl -sSL https://install.python-poetry.org | python3 -
/root/.local/bin/poetry --version
export PATH="/root/.local/bin:$PATH"
poetry --version
```

- Install Project

```
git clone https://github.com/marcraft2/MusicReleaseAlert.git
cd MusicReleaseAlert
poetry install
```


- Set Configuration

```
mkdir /etc/MusicReleaseAlert
nano /etc/MusicReleaseAlert/MusicReleaseAlert.cfg
```

```
[MusicReleaseAlert]
spotify_client_id: xxxx
spotify_client_secret: xxxx
spotify_redirect_uri: https://xxxxx.wtf
database_file: /var/MusicReleaseAlert/spotify.db
telegram_token: XXXXX
```

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

- Manual Run
```
cd /usr/local/MusicReleaseAlert && /root/.local/bin/poetry run MusicReleaseAlert
```

- Set cron (auto run every 10 minutes)

```
crontab -e
```

```
2,12,22,32,42,52 * * * * cd /usr/local/MusicReleaseAlert && /root/.local/bin/poetry run MusicReleaseAlert >> /var/log/MusicReleaseAlert.log 2>&1
```
