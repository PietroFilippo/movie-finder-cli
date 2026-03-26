"""Anime torrent provider — searches video and TV categories."""

from providers.base import BaseProvider


class AnimeProvider(BaseProvider):
    name = "Anime"
    icon = "🍙"
    categories = [201, 205, 207, 208]  # Movies, TV, HD Movies, HD TV
