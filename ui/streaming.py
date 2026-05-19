"""Terminal-UX primitives for the streaming flow.

Pinned-header rendering, scroll-region pinning, terminal-title escape codes,
and screen-clear helpers used by ``stream_with_webtorrent`` and
``stream_with_peerflix`` in ``downloader.py``. Stream-flow shaped: the
header knows about episode index, VLC URL, and attached sub paths — not a
generic terminal toolkit.
"""

import os
import sys

from constants import console


# Fixed header height for multi-episode streaming. We always reserve this
# many lines so the scroll region boundary never shifts between episodes.
_STREAM_HEADER_LINES = 7


def _clear_terminal() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def _set_terminal_title(title: str) -> None:
    """Set the terminal window title via OSC escape."""
    sys.stdout.write(f"\033]0;{title}\007")
    sys.stdout.flush()


def _print_stream_header(
    ep_idx: int,
    total: int,
    file_idx: int | None,
    multi: bool,
    vlc_url: str | None = None,
    use_scroll_region: bool = True,
    sub_paths: list[str] | None = None,
) -> None:
    """Print the episode header and optionally pin it with a scroll region.

    When *use_scroll_region* is True (peerflix), the header is pinned at
    the top of the terminal and a scroll region is set below it.
    When False (webtorrent), only the terminal **window title** is used
    for persistent episode info, since webtorrent's ANSI rendering
    clears through scroll regions.

    ``sub_paths``, if provided, is shown as a one-line confirmation that
    subtitles will be attached to VLC for this episode.
    """
    # Reset any previous scroll region so clear works on the full screen
    sys.stdout.write("\033[r")
    sys.stdout.flush()
    _clear_terminal()

    n = ep_idx + 1

    # Always set the terminal title — persists regardless of screen content
    if multi:
        _set_terminal_title(f"Episode {n}/{total} — file {file_idx} | n: next  b: back  v: VLC  Ctrl+C: cancel")
    elif file_idx is not None:
        _set_terminal_title(f"Streaming file {file_idx} | v: VLC  Ctrl+C: cancel")

    # Build header lines
    lines: list[str] = []
    if multi:
        lines.append(f"[info]Episode {n}/{total} — file index {file_idx}[/info]")
    elif file_idx is not None:
        lines.append(f"[info]Streaming file index:[/info] [highlight]{file_idx}[/highlight]")
    lines.append("[bold red]CTRL+C to cancel.[/bold red]")
    if vlc_url:
        lines.append("[bold yellow]Press 'v' to reopen VLC without losing download progress.[/bold yellow]")
    if multi:
        lines.append("[bold yellow]Press 'n' to skip to the next episode.[/bold yellow]")
        if ep_idx > 0:
            lines.append("[bold yellow]Press 'b' to go back to the previous episode (will re-download).[/bold yellow]")
        lines.append("[dim]VLC will be closed automatically when switching episodes.[/dim]")
    if sub_paths:
        primary = os.path.basename(sub_paths[0])
        extras = f" (+{len(sub_paths) - 1} more)" if len(sub_paths) > 1 else ""
        lines.append(f"[success]📝 Subtitles attached:[/success] [highlight]{primary}[/highlight]{extras}")

    # Print the header lines
    for line in lines:
        console.print(line)

    if use_scroll_region:
        # Pad to fixed height so the scroll region boundary is stable
        for _ in range(len(lines), _STREAM_HEADER_LINES):
            console.print()
        # Set scroll region: rows _STREAM_HEADER_LINES+1 .. terminal height
        term_h = console.size.height
        top = _STREAM_HEADER_LINES + 1
        if top < term_h:
            sys.stdout.write(f"\033[{top};{term_h}r")
            # Move cursor into the scroll region and clear it
            sys.stdout.write(f"\033[{top};1H")
            sys.stdout.write("\033[J")  # erase from cursor to end of region
            sys.stdout.flush()
    else:
        console.print()  # just a blank separator line


def _reset_scroll_region() -> None:
    """Remove the scroll region so the full terminal is usable again."""
    sys.stdout.write("\033[r")
    sys.stdout.flush()


def _reset_terminal_title() -> None:
    """Restore the terminal title to the default."""
    _set_terminal_title("Torrent Search CLI")
