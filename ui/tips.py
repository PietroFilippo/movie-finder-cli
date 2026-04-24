"""Rotating tip pool shown on menu screens — reminds users about non-obvious
hotkeys, persisted behavior, and safety notes without stealing attention.

Tips are rendered in dim italic with a small cyan "💡 Tip:" prefix so they
read as a hint, not a primary action.
"""

import random


TIPS: list[str] = [
    "For best results, search using the complete release name.",
    "Press Shift+F at the search prompt to tweak engines or toggle filter presets.",
    "Press F on a highlighted provider to configure its filters without leaving this menu.",
    "aria2c is the fastest downloader — it handles multi-file selection in a single process.",
    "Toggle 🔇 Quiet mode in the download menu to replace subprocess UIs with a minimal spinner.",
    "Press v while streaming to reopen VLC without killing the torrent session.",
    "Multi-episode streams: press n for next, b for previous episode.",
    "Shift+H opens your search history — past queries re-run with one keypress.",
    "Shift+S shows usage stats: runtime, top queries, method completion rates.",
    "Anime episode picker: v sets an anchor, Shift+V mass-toggles the range between anchor and cursor.",
    "Filter menu keybinds: a select all • i invert • c clear presets • w save.",
    "Your engine + preset toggles persist across runs in filter_state.json.",
    "Use -f and -x on the CLI to add ad-hoc include/exclude keywords.",
    "Your public IP is visible to every peer — a VPN is the only real mitigation.",
    "The 'Trusted Uploaders' preset is a community reputation heuristic, not a safety guarantee.",
    "Results are deduped by info hash across engines, then sorted by seeders.",
]


def random_tip() -> str:
    """Return a randomly-picked tip rendered as Rich markup.

    The prefix is cyan italic to catch the eye; the body is dim italic so it
    stays a hint, not a header. Safe to drop into an `arrow_select` footer.
    """
    text = random.choice(TIPS)
    return f"[italic cyan]💡 Tip:[/italic cyan] [dim italic]{text}[/dim italic]"
