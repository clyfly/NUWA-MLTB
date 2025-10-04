# NUWA MLTB
![Header Image](https://i.pinimg.com/736x/9f/76/95/9f76951599947bb26da66feb7cb1e5fa.jpg)

**This is the official repository.** Maintained by [![Telegram](https://img.shields.io/badge/Telegram-%40clyfly-blue.svg?style=flat&logo=telegram)](https://t.me/clyfly)

## Description
This is a Telegram Bot for mirroring and leeching files from the internet to Google Drive, Telegram, or other rclone-supported clouds. It's a fork of [@anasty17's mirror-leech-telegram-bot](https://github.com/anasty17/mirror-leech-telegram-bot), built with Python and asynchronous programming. Supports torrents, direct links, YouTube-dl sites, and more using tools like qBittorrent, Aria2c, Sabnzbd, JDownloader, and yt-dlp.  

The original repo was strictly **VPS-only** (because apparently running a bot should feel like a luxury 🙄). This fork exists because Heroku with container stack is cheaper, simpler, and honestly enough for most use cases.

## Key Features
- Mirror/leech files from various sources (torrents, links, YouTube, etc.).
- Integration with Google Drive: upload, download, clone, delete, and search.
- Rclone support for cloud transfers with custom configs and flags.
- Queue system for tasks, status monitoring, and RSS feeds.
- Archive/extract files with passwords.
- Customizable uploads: thumbnails, prefixes, splits, and more.
- Bot settings stored in MongoDB for persistence.

## Heroku Deployment
This fork is optimized for deployment on **Heroku using Docker/Container stack**. Just fork this repo, adjust `config_sample.py` → `config.py`, and make sure `Dockerfile` + `heroku.yml` exist.

## Usage
Generate session strings, tokens, and service accounts. Set bot commands in [@BotFather](https://t.me/BotFather). Start the bot and use `/mirror`, `/leech`, etc.

## Dependencies
- API_ID, API_HASH & BOT_TOKEN
- Heroku cli or similar tools
- A working brain 
- External: MongoDB, Google Drive API, rclone, qBittorrent/Aria2c.  

## Big Credits
Big credits to the original [@anasty17/mirror-leech-telegram-bot](https://github.com/anasty17/mirror-leech-telegram-bot).  

Without the OG, there’d be nothing to sarcastically “fix for Heroku containers.” 😅