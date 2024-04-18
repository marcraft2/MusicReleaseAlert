# Music Release Twitter Alert

## Twitter

- https://twitter.com/MusicReleaseFR
- https://twitter.com/MusicReleaseUS

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

- Generate Twitter API Key

Get your CONSUMER_KEY and CONSUMER_SECRET on [Developer Twitter Website](https://developer.twitter.com/en/portal/projects-and-apps)

```
export 'CONSUMER_KEY'='<your_consumer_key>'
export 'CONSUMER_SECRET'='<your_consumer_secret>'
python3 gen_twitter_key.py
```

Open the link, in your browser, with the account you wanted to tweet from. And Copy/Paste PIN code to terminal.
Now copy your xx_twitter_consumer_key, xx_twitter_consumer_secret, xx_twitter_access_token, xx_twitter_access_token_secret for next step.


For Spotify access, I recommend that you start the program for the first time on your machine, to generate the .cache file, once this file is created you can place it directly in the /usr/local/MusicReleaseAlert folder.



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

- Set cron (auto run every 20 minutes)

```
crontab -e
```

```
2,12,22,32,42,52 * * * * cd /usr/local/MusicReleaseAlert && /root/.local/bin/poetry run MusicReleaseAlert >> /var/log/MusicReleaseAlert.log 2>&1
```
