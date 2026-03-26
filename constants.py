"""Shared constants, theme, and console instance."""

import os

from rich.console import Console
from rich.theme import Theme

# Theme & Console
custom_theme = Theme(
    {
        "title": "bold magenta",
        "info": "dim cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "highlight": "bold white",
    }
)

console = Console(theme=custom_theme)

# API
API_URL = "https://apibay.org/q.php"
RESULTS_PER_PAGE = 20
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.bittor.pw:1337/announce",
    "udp://public.popcorn-tracker.org:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://exodus.desync.com:6969",
    "udp://open.demonii.com:1337/announce",
]

# Apibay category IDs
CATEGORIES = {
    # Video
    "video_all": 200,
    "video_movies": 201,
    "video_tv": 205,
    "video_hd_movies": 207,
    "video_hd_tv": 208,
    # Games
    "games_all": 400,
    "games_pc": 401,
    "games_mac": 402,
    "games_psx": 403,
    "games_xbox": 404,
    "games_wii": 405,
    "games_handheld": 406,
    "games_ios": 407,
    "games_android": 408,
}
