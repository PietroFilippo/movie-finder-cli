"""Game torrent provider — searches PC game categories."""

from providers.base import BaseProvider


class GameProvider(BaseProvider):
    name = "Games"
    icon = "🎮"
    categories = [400, 401]  # Games All, PC Games

    def search(self, query: str) -> list[dict]:
        """Search and filter out 'Update Only' and 'Update v' results by default."""
        results = super().search(query)
        
        filtered = []
        for r in results:
            name = r.get("name", "").lower()
            if "update only" in name or "update v" in name:
                continue
            filtered.append(r)
            
        return filtered
