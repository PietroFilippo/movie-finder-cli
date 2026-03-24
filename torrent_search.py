#!/usr/bin/env python3
"""
Torrent Search CLI — Search for torrents and download via magnet link.

Usage:
    python torrent_search.py              # Interactive prompt
    python torrent_search.py -q "query"   # Direct search
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import textwrap

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
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

# Constants
API_URL = "https://apibay.org/q.php"
MAX_RESULTS = 20

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


# Utilities
def format_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    if size_bytes <= 0:
        return "N/A"
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    size = float(size_bytes)
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.1f} {units[idx]}"


def seed_style(seeds: int) -> str:
    """Return a rich color tag based on seed count."""
    if seeds >= 50:
        return "bold green"
    elif seeds >= 10:
        return "green"
    elif seeds >= 1:
        return "yellow"
    return "red"


def leech_style(leeches: int) -> str:
    """Return a rich color tag based on leech count."""
    if leeches <= 5:
        return "dim white"
    elif leeches <= 50:
        return "yellow"
    return "red"


def build_magnet(info_hash: str, name: str) -> str:
    """Build a magnet URI from an info hash."""
    trackers = "&".join(f"tr={t}" for t in TRACKERS)
    return f"magnet:?xt=urn:btih:{info_hash}&dn={name}&{trackers}"


def open_magnet(magnet_link: str) -> None:
    """Open a magnet link with the system default handler (qBittorrent, etc.)."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(magnet_link)
        elif system == "Darwin":
            subprocess.Popen(["open", magnet_link])
        else:
            subprocess.Popen(["xdg-open", magnet_link])
    except Exception as e:
        console.print(f"[error]✗ Failed to open magnet link: {e}[/error]")
        console.print(f"[info]Magnet link:[/info] {magnet_link}")


# API


def search_torrents(query: str) -> list[dict]:
    """Search apibay.org and return a list of torrent dicts."""
    try:
        response = requests.get(API_URL, params={"q": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        console.print(f"[error]✗ API request failed: {e}[/error]")
        return []
    except ValueError:
        console.print("[error]✗ Invalid response from API.[/error]")
        return []

    # apibay returns [{"id": "0", "name": "No results ..."}] when nothing is found
    if not data or (len(data) == 1 and data[0].get("id") == "0"):
        return []

    return data[:MAX_RESULTS]


# Display
def display_results(results: list[dict]) -> Table:
    """Build and print a rich table of torrent results. Returns the table."""
    table = Table(
        title="🔍 Torrent Results",
        title_style="bold magenta",
        border_style="bright_blue",
        header_style="bold cyan",
        row_styles=["", "dim"],
        show_lines=False,
        padding=(0, 1),
    )

    table.add_column("#", style="bold white", justify="right", width=4)
    table.add_column("Name", style="white", max_width=60, no_wrap=False)
    table.add_column("Size", style="cyan", justify="right", width=10)
    table.add_column("Seeds", justify="right", width=7)
    table.add_column("Leeches", justify="right", width=9)

    for i, item in enumerate(results):
        seeds = int(item.get("seeders", 0))
        leeches = int(item.get("leechers", 0))
        size = int(item.get("size", 0))
        name = item.get("name", "Unknown")

        table.add_row(
            str(i),
            name,
            format_size(size),
            f"[{seed_style(seeds)}]{seeds}[/{seed_style(seeds)}]",
            f"[{leech_style(leeches)}]{leeches}[/{leech_style(leeches)}]",
        )

    console.print()
    console.print(table)
    console.print()

    return table


# Selection (fzf)
def select_with_fzf(results: list[dict]) -> int | None:
    """
    Pipe results into fzf for interactive selection.
    Returns the index of the selected result, or None if cancelled.
    """
    fzf_path = shutil.which("fzf")
    if not fzf_path:
        console.print(
            "[warning] fzf not found. Falling back to manual input.[/warning]"
        )
        return select_manual(results)

    # Build lines for fzf: "index | name | size | seeds"
    lines = []
    for i, item in enumerate(results):
        name = item.get("name", "Unknown")
        seeds = item.get("seeders", 0)
        size = format_size(int(item.get("size", 0)))
        lines.append(f"{i:>3} │ {name} │ {size} │ S:{seeds}")

    fzf_input = "\n".join(lines)

    try:
        result = subprocess.run(
            [
                fzf_path,
                "--height=40%",
                "--reverse",
                "--border=rounded",
                "--prompt=Select torrent > ",
                "--header=↑/↓ navigate  |  Enter select  |  Esc cancel",
                "--color=fg:#c0caf5,bg:#1a1b26,hl:#bb9af7",
                "--color=fg+:#c0caf5,bg+:#292e42,hl+:#7dcfff",
                "--color=info:#7aa2f7,prompt:#7dcfff,pointer:#ff007c",
                "--color=marker:#9ece6a,spinner:#9ece6a,header:#9ece6a",
            ],
            input=fzf_input,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # User pressed Esc or Ctrl+C
            return None

        selected_line = result.stdout.strip()
        # Extract the index from the start of the line
        idx = int(selected_line.split("│")[0].strip())
        return idx

    except (subprocess.SubprocessError, ValueError, IndexError):
        console.print("[warning] fzf error. Falling back to manual input.[/warning]")
        return select_manual(results)


def select_manual(results: list[dict]) -> int | None:
    """Fallback manual selection when fzf is not available."""
    try:
        raw = console.input("[info]Enter torrent #[/info] (or 'q' to cancel): ")
        if raw.strip().lower() in ("q", "quit", "exit"):
            return None
        idx = int(raw.strip())
        if 0 <= idx < len(results):
            return idx
        console.print(f"[error] Invalid index. Must be 0–{len(results) - 1}.[/error]")
        return None
    except (ValueError, EOFError):
        return None


# Main Loop
def print_banner() -> None:
    banner = Text()
    banner.append("Torrent Search CLI", style="bold magenta")
    console.print(
        Panel(
            banner,
            border_style="bright_blue",
            padding=(1, 2),
        )
    )
    console.print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Search and download torrents.")
    parser.add_argument("-q", "--query", type=str, help="Search query (skip prompt)")
    args = parser.parse_args()

    print_banner()

    query = args.query

    while True:
        # Get query
        if not query:
            try:
                query = console.input("[title] Search torrent:[/title] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[info]Goodbye![/info]")
                break

        if not query:
            console.print("[warning] Please enter a search term.[/warning]")
            query = None
            continue

        # Search
        console.print(f"[info]Searching for:[/info] [highlight]{query}[/highlight]…")

        results = search_torrents(query)
        if not results:
            console.print("[warning] No results found.[/warning]\n")
            query = None
            continue

        # Display
        display_results(results)

        # Select
        idx = select_with_fzf(results)
        if idx is None:
            console.print("[info]Selection cancelled.[/info]\n")
            query = None
            continue

        selected = results[idx]
        name = selected.get("name", "Unknown")
        info_hash = selected.get("info_hash", "")

        console.print(f"\n[success] Selected:[/success] [highlight]{name}[/highlight]")

        # Download
        magnet = build_magnet(info_hash, name)
        console.print("[info]Opening magnet link with default torrent client…[/info]")
        open_magnet(magnet)
        console.print("[success] Magnet link sent to torrent client![/success]\n")

        # Continue?
        try:
            again = console.input("[info]Search again? (Y/n):[/info] ").strip().lower()
            if again in ("n", "no"):
                console.print("[info]Goodbye![/info]")
                break
        except (EOFError, KeyboardInterrupt):
            console.print("\n[info]Goodbye![/info]")
            break

        query = None


if __name__ == "__main__":
    main()
