# Spotify Twitter Alert

Create Database:

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
