
# Plex to Letterboxd Sync

This tool automatically syncs your watched movies from Plex to Letterboxd. It extracts your watched movie history from Plex, including titles, years, directors, and watch dates, then uploads this information to your Letterboxd account.


## Prerequisites

- A Plex server with a movies library
- A Letterboxd account
- Docker and Docker Compose (for Docker deployment)

## Configuration

The following environment variables are required:

- `PLEX_URL`: Your Plex server URL (e.g., `http://localhost:32400`)
- `PLEX_TOKEN`: Your Plex authentication token
- `LETTERBOXD_EMAIL`: Your Letterboxd account email
- `LETTERBOXD_PASSWORD`: Your Letterboxd account password

### Getting Your Plex Token

1. Log in to Plex Web App (app.plex.tv)
2. Play any video
3. While the video is playing, right-click and select "Get Info" or press `i`
4. In the window that opens, click the "View XML" button
5. In the URL of the new page that opens, look for `X-Plex-Token=`. The string after this is your Plex token
