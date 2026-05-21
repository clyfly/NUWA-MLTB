# CLYFLY MLTB

[![Telegram](https://img.shields.io/badge/Telegram-%40clyfly-blue.svg?style=flat&logo=telegram)](https://t.me/clyfly)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=flat&logo=python)
![Docker](https://img.shields.io/badge/Docker-Container-blue.svg?style=flat&logo=docker)
![Heroku](https://img.shields.io/badge/Heroku-Deployed-purple.svg?style=flat&logo=heroku)
![License](https://img.shields.io/badge/License-GPL--3.0-red.svg?style=flat)

![Header Image](https://i.pinimg.com/736x/9f/76/95/9f76951599947bb26da66feb7cb1e5fa.jpg)

> A Heroku-optimized fork of [@anasty17's mirror-leech-telegram-bot](https://github.com/anasty17/mirror-leech-telegram-bot), maintained by [@clyfly](https://t.me/clyfly).

---

## Table of Contents

- [Description](#description)
- [Key Features](#key-features)
- [Bot Commands](#bot-commands)
- [Heroku Deployment](#heroku-deployment)
- [Configuration](#configuration)
- [Credits](#credits)

---

## Description

CLYFLY MLTB is a Telegram bot for mirroring and leeching files from the internet to Google Drive, Telegram, or any rclone-supported cloud storage. Built on Python with asynchronous programming, it supports torrents, direct links, all yt-dlp supported sites, Usenet (NZB), and JDownloader — powered by qBittorrent, Aria2c, Sabnzbd, and yt-dlp under the hood.

The original repository was designed strictly for VPS deployments. This fork exists to make it run on **Heroku using Docker/Container stack** — cheaper, simpler, and more than enough for most use cases.

The key difference in this fork is that the `bot/` directory is intentionally left empty in the repository. On startup, `update.py` automatically pulls the bot source from `UPSTREAM_REPO`, which prevents a crash that consistently occurs on Heroku when the folder is present during the initial deploy. The exact cause is unclear, but removing it fixes it — and that's good enough. All bot and user settings are persisted in MongoDB across restarts.

---

## Key Features

- Mirror and leech from multiple sources: torrents, direct links, YouTube, Usenet (NZB), JDownloader, and all yt-dlp supported sites.
- Full Google Drive integration: upload, download, clone, delete, count, and search.
- Rclone support for transfers to any supported cloud with custom config and flags.
- Queue system, real-time status monitoring, and automated RSS feeds.
- Archive and extract files with optional password support.
- Highly customizable uploads: thumbnails, filename prefix, split size, media groups, dump chat, and more.
- All bot and user settings stored in MongoDB for persistence across restarts.
- Auto-update from `UPSTREAM_REPO` on every restart — no manual rebuilds needed.

---

## Bot Commands

Set these commands via [@BotFather](https://t.me/BotFather):

> **Note:** JDownloader (`jdmirror`, `jdleech`) and Sabnzbd/Usenet (`nzbmirror`, `nzbleech`) are available but **not guaranteed to be stable on Heroku** due to its limited resources. Use them at your own risk — other download methods are recommended for day-to-day use.

```
mirror - or /m Mirror to cloud storage
qbmirror - or /qm Mirror torrent via qBittorrent
jdmirror - or /jm Mirror via JDownloader ⚠️ may be unstable on Heroku
nzbmirror - or /nm Mirror via Sabnzbd (Usenet) ⚠️ may be unstable on Heroku
ytdl - or /y Mirror from yt-dlp supported sites
leech - or /l Upload to Telegram
qbleech - or /ql Leech torrent via qBittorrent
jdleech - or /jl Leech via JDownloader ⚠️ may be unstable on Heroku
nzbleech - or /nl Leech via Sabnzbd (Usenet) ⚠️ may be unstable on Heroku
ytdlleech - or /yl Leech from yt-dlp supported sites
clone - Copy file/folder in Google Drive
count - Count files/folders in Google Drive
usetting - or /us User settings
bsetting - or /bs Bot settings
status - View status of all active tasks
sel - Select files from torrent before download
rss - RSS feed menu
list - Search files in Google Drive
search - Search torrents via API
cancel - or /c Cancel a task
cancelall - Cancel all active tasks
forcestart - or /fs Force start a task from queue
del - Delete file/folder from Google Drive
log - View bot logs
auth - Authorize a user or chat
unauth - Unauthorize a user or chat
shell - Run shell commands
restart - Restart the bot
stats - View bot usage statistics
ping - Ping the bot
help - List all commands with descriptions
```

---

## Heroku Deployment

This fork is optimized for **Heroku using Docker/Container stack**. Make sure to set the stack to `container` — not Heroku's default stack.

### How It Works

On startup, `update.py` pulls the bot source into the `bot/` directory from the URL set in `UPSTREAM_REPO`. This is why the `bot/` folder must be absent from your fork — leaving it in causes a crash on the initial Heroku deploy for reasons that aren't entirely clear, but removing it consistently resolves the issue. Once the pull completes, `start.sh` runs the bot.

### Deployment Steps

1. **Fork this repository** to your own GitHub account.

2. **Delete the `bot/` folder** from your fork. It will be populated automatically at runtime via `UPSTREAM_REPO`.

3. **Configure the bot:**
   - Rename `config_sample.py` → `config.py`
   - Fill in at least the required fields (see [Configuration](#configuration) below)
   - Set `UPSTREAM_REPO` to your fork URL so the bot always pulls the latest version on restart

4. **Create a Heroku app** and connect it to your forked repository.

5. **Set the stack to container:**
   ```bash
   heroku stack:set container -a your-app-name
   ```

6. **Deploy** via the Heroku dashboard (Connect to GitHub → Enable Automatic Deploys), or via CLI:
   ```bash
   git push heroku master
   ```

7. Confirm that `Dockerfile` and `heroku.yml` exist in the root of your repo — they should be there unless you deleted them. ✅

---

## Koyeb Deployment

This repo now supports deployment on Koyeb using the existing `Dockerfile`.

### How to deploy on Koyeb

1. Push the repository to GitHub.
2. Create a new Koyeb app and choose "Deploy from a Git repository".
3. Select this repository and use the root `Dockerfile` as the build context.
4. Add the required environment variables in Koyeb:
   - `BOT_TOKEN`
   - `OWNER_ID`
   - `TELEGRAM_API`
   - `TELEGRAM_HASH`
   - `UPSTREAM_REPO` (your repo URL, if you want automatic updates)
   - `UPSTREAM_BRANCH` (default: `master`)
   - `DATABASE_URL` (optional, for MongoDB persistence)

### Notes for Koyeb

- `config.py` is optional when deploying on Koyeb. The bot can start from environment variables if `config.py` is not present.
- The `Dockerfile` now uses a standard Python container and installs required build dependencies.
- If you need custom settings beyond the required environment variables, you can still add a local `config.py` in your repository.
- The container exposes `8070` and `8080` so Koyeb can attach a web route if needed.

---

## Configuration

Copy `config_sample.py` to `config.py` and fill in the values. For the full list of all available variables, refer to `config_sample.py` directly.

### Required

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Your Telegram user ID (not username) |
| `TELEGRAM_API` | API ID from [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_HASH` | API Hash from [my.telegram.org](https://my.telegram.org) |

### Optional but Recommended

| Variable | Description |
|---|---|
| `DATABASE_URL` | MongoDB connection URI for storing bot and user settings |
| `UPSTREAM_REPO` | Your GitHub fork URL for auto-update on restart |
| `GDRIVE_ID` | Google Drive folder or TeamDrive ID for uploads |
| `RCLONE_PATH` | Default rclone remote path for uploads |
| `DEFAULT_UPLOAD` | `rc` for rclone, `gd` for Google Drive |
| `LEECH_DUMP_CHAT` | Chat ID where leeched files will be sent |
| `USER_SESSION_STRING` | Pyrogram user session for premium Telegram features |
| `AUTHORIZED_CHATS` | Space-separated chat or user IDs allowed to use the bot |

---

## Credits

All credit goes to the original [@anasty17/mirror-leech-telegram-bot](https://github.com/anasty17/mirror-leech-telegram-bot) — the foundation this fork is built on. This project is licensed under the [GPL-3.0 License](https://github.com/anasty17/mirror-leech-telegram-bot/blob/master/LICENSE), same as the upstream repository.

Without it, there would be nothing to sarcastically fix for Heroku containers. 😅