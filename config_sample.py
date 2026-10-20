# REQUIRED CONFIG
BOT_TOKEN = ""
OWNER_ID = 0
TELEGRAM_API = 0
TELEGRAM_HASH = ""
# OPTIONAL CONFIG
TG_PROXY = {}
USER_SESSION_STRING = ""
CMD_SUFFIX = ""
AUTHORIZED_CHATS = ""
SUDO_USERS = ""
DATABASE_URL = ""
DATABASE_NAME = "mltb"
# Delete task commands and replied-to source messages for download/clone tasks.
DELETE_LINKS = False
STATUS_LIMIT = 4
DEFAULT_UPLOAD = "rc"
STATUS_UPDATE_INTERVAL = 15
FILELION_API = ""
STREAMWISH_API = ""
ALLDEBRID_API_KEY = ""
BUZZHEAVIER_ACCOUNT_ID = ""
BUZZHEAVIER_FOLDER_ID = ""
GOFILE_API_KEY = ""
TLDV_TOKEN = ""
EXCLUDED_EXTENSIONS = ""
INCLUDED_EXTENSIONS = ""
INCOMPLETE_TASK_NOTIFIER = False
YT_DLP_OPTIONS = ""
GALLERY_DL_OPTIONS = ""
USE_SERVICE_ACCOUNTS = False
NAME_SUBSTITUTE = r""
FFMPEG_CMDS = {"merge": ["-f concat -safe 0 -i mltb.txt -c copy mltb.mp4 -del"]}
# Metadata values are FFmpeg tags; templates support {filename}, {basename},
# {extension}, {audiolang}, {sublang}, and {year}.
# Example: {"title": "{basename}", "date": "{year}"}
METADATA = {}
# Example: {"title": "{basename} ({audiolang})"}
AUDIO_METADATA = {}
# Example: {"title": "{basename} ({year})"}
VIDEO_METADATA = {}
# Example: {"title": "Subtitles ({sublang})"}
SUBTITLE_METADATA = {}
UPLOAD_PATHS = {}
# GDrive Tools
GDRIVE_ID = ""
IS_TEAM_DRIVE = False
STOP_DUPLICATE = False
INDEX_URL = ""
# Rclone
RCLONE_PATH = ""
RCLONE_FLAGS = ""
RCLONE_SERVE_URL = ""
RCLONE_SERVE_PORT = 0
RCLONE_SERVE_USER = ""
RCLONE_SERVE_PASS = ""
# JDownloader
JD_EMAIL = ""
JD_PASS = ""
# Sabnzbd
USENET_SERVERS = [
    {
        "name": "main",
        "host": "",
        "port": 563,
        "timeout": 60,
        "username": "",
        "password": "",
        "connections": 8,
        "ssl": 1,
        "ssl_verify": 2,
        "ssl_ciphers": "",
        "enable": 1,
        "required": 0,
        "optional": 0,
        "retention": 0,
        "send_group": 0,
        "priority": 0,
    }
]
# Nzb search
HYDRA_IP = ""
HYDRA_API_KEY = ""
# Update
UPSTREAM_REPO = ""
UPSTREAM_BRANCH = "master"
# Leech
LEECH_SPLIT_SIZE = 0
MIN_LEECH_UPLOAD_SIZE = 0
AS_DOCUMENT = False
EQUAL_SPLITS = False
MEDIA_GROUP = False
USER_TRANSMISSION = False
HYBRID_LEECH = False
# Example: "<b>{filename}</b>\nSize: {size}\n{precaption}"
# Also supports {duration}, {quality}, {languages}, {subtitles}, {md5_hash},
# {mime_type}, and {prefilename}. User-specific captions take precedence.
LEECH_CAPTION = ""
LEECH_FILENAME_PREFIX = ""
LEECH_DUMP_CHAT = ""
CLONE_DUMP_CHATS = ""
THUMBNAIL_LAYOUT = ""
FILES_LINKS = False
# qBittorrent/Aria2c
DISABLE_SEED = False
TORRENT_TIMEOUT = 0
BASE_URL = ""
BASE_URL_PORT = 0
WEB_PINCODE = False
# Queueing system
QUEUE_ALL = 0
QUEUE_DOWNLOAD = 0
QUEUE_UPLOAD = 0
# Task limits (0 = disabled)
BOT_TASK_LIMIT = 0  # Max total concurrent tasks for the entire bot
USER_TASK_LIMIT = 0  # Max concurrent tasks per user
# File deduplication (skip downloading files already downloaded recently)
DEDUP_ENABLED = False
# Bot language (en, hi, ar, id, tr, pt, bn)
BOT_LANGUAGE = "en"
# RSS
RSS_DELAY = 600
RSS_CHAT = ""
RSS_SIZE_LIMIT = 0
# Torrent Search
SEARCH_API_LINK = ""
SEARCH_LIMIT = 0
# Rate Limiting (commands per user per window, 0 = disabled)
RATE_LIMIT_PER_MIN = 0
RATE_LIMIT_WINDOW = 60

SEARCH_PLUGINS = [
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/piratebay.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/limetorrents.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torlock.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentscsv.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/eztv.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentproject.py",
    "https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engines/master/kickass_torrent.py",
    "https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engines/master/yts_am.py",
    "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/linuxtracker.py",
    "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/nyaasi.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/ettv.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/glotorrents.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/thepiratebay.py",
    "https://raw.githubusercontent.com/v1k45/1337x-qBittorrent-search-plugin/master/leetx.py",
    "https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/magnetdl.py",
    "https://raw.githubusercontent.com/msagca/qbittorrent_plugins/main/uniondht.py",
    "https://raw.githubusercontent.com/khensolomon/leyts/master/yts.py",
]
