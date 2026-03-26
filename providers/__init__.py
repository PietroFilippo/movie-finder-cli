"""Provider registry - import and expose all available providers."""

from providers.anime_provider import AnimeProvider
from providers.game_provider import GameProvider
from providers.movie_provider import MovieProvider

# Registry of all available providers (order = display order)
PROVIDERS: list = [
    MovieProvider(),
    GameProvider(),
    AnimeProvider(),
]

def get_provider(name: str):
    """Look up a provider by name (case-insensitive, allows prefix like 'game' for 'Games')."""
    for p in PROVIDERS:
        if p.name.lower().startswith(name.lower()):
            return p
    return None
