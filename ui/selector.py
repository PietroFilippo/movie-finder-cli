"""Reusable arrow-key interactive selector using Rich Live + readchar"""

from dataclasses import dataclass, field

import readchar
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from constants import console


@dataclass
class SelectItem:
    """A single item in the selector list"""
    label: str
    value: object = None
    enabled: bool = True
    toggled: bool = False
    hint: str = ""  # Dim subtext shown below the label


def _build_panel(
    items: list[SelectItem],
    cursor: int,
    title: str,
    multi: bool,
    footer: str = "",
) -> Panel:
    """Render the selector as a Rich Panel"""
    body = Text()

    for i, item in enumerate(items):
        is_cursor = i == cursor

        # Build the prefix
        if multi:
            check = "✓" if item.toggled else " "
            if is_cursor:
                prefix = f"  ❯ [{check}] "
            else:
                prefix = f"    [{check}] "
        else:
            if is_cursor:
                prefix = "  ❯ "
            else:
                prefix = "    "

        # Determine style
        if not item.enabled:
            style = "dim strikethrough" if is_cursor else "dim"
        elif is_cursor:
            style = "bold cyan"
        else:
            style = "white"

        body.append(prefix, style=style)
        body.append(item.label, style=style)

        # Show hint if present
        if item.hint:
            body.append(f"  {item.hint}", style="dim yellow")

        body.append("\n")

    # Footer / help text
    if not footer:
        if multi:
            footer = "↑/↓ navigate  •  Space toggle  •  Enter confirm  •  Esc cancel"
        else:
            footer = "↑/↓ navigate  •  Enter select  •  Esc cancel"

    body.append("\n")
    body.append(f" {footer}", style="dim")

    return Panel(
        body,
        title=f"[bold magenta]{title}[/bold magenta]",
        border_style="bright_blue",
        padding=(1, 2),
    )


def _next_enabled(items: list[SelectItem], current: int, direction: int) -> int:
    """Move to the next enabled item in the given direction, wrapping around."""
    n = len(items)
    pos = current
    for _ in range(n):
        pos = (pos + direction) % n
        if items[pos].enabled:
            return pos
    return current  # All disabled - stay put


def arrow_select(
    items: list[SelectItem],
    title: str = "Select",
    multi: bool = False,
    footer: str = "",
    start_index: int = 0,
) -> int | list[int] | None:
    """Interactive arrow-key selector.

    Args:
        items: List of SelectItem to display.
        title: Panel title.
        multi: If True, Space toggles items and Enter confirms the toggled set.
               Returns a list of indices of toggled items (may be empty).
               If False, Enter returns the index of the highlighted item.
        footer: Custom footer text (overrides default).
        start_index: Initial cursor position.

    Returns:
        - Single-select mode: index of chosen item, or None if cancelled.
        - Multi-toggle mode: list of indices of toggled items, or None if cancelled.
    """
    if not items:
        return None

    # Ensure cursor starts on an enabled item
    cursor = start_index
    if not items[cursor].enabled:
        cursor = _next_enabled(items, cursor, 1)

    # Track terminal size to detect resize events
    prev_size = console.size

    with Live(
        _build_panel(items, cursor, title, multi, footer),
        console=console,
        refresh_per_second=15,
        transient=True,
    ) as live:
        while True:
            key = readchar.readkey()

            if key == readchar.key.UP:
                cursor = _next_enabled(items, cursor, -1)
            elif key == readchar.key.DOWN:
                cursor = _next_enabled(items, cursor, 1)
            elif key in (readchar.key.ENTER, readchar.key.CR, readchar.key.LF):
                if multi:
                    return [i for i, it in enumerate(items) if it.toggled]
                else:
                    if items[cursor].enabled:
                        return cursor
            elif key == " " and multi:
                if items[cursor].enabled:
                    items[cursor].toggled = not items[cursor].toggled
            elif key == readchar.key.ESC:
                return None
            elif key in (readchar.key.CTRL_C, "\x03"):
                return None

            # On terminal resize, clear screen to prevent ghost panels
            current_size = console.size
            if current_size != prev_size:
                prev_size = current_size
                console.clear()

            live.update(_build_panel(items, cursor, title, multi, footer))

    return None
