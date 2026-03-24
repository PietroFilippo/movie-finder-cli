---
name: Torrent Search CLI
description: A command-line torrent search & download tool using Python, fzf, and rich tables
---

# Torrent Search CLI

A command-line application to search for torrents by name, view results in a styled table, select via fuzzy finder, and download via magnet link.

## Tech Stack

- **Python 3.11+** — core application logic
- **rich** — styled tables, panels, and colored output
- **requests** — HTTP calls to the torrent API
- **fzf** — interactive fuzzy finder for torrent selection
- **qBittorrent** (or any default torrent client) — handles magnet link downloads

## Project Structure

```
torrent/
├── torrent_search.py     # Main application
├── torrent.bat            # Windows launcher
├── requirements.txt       # Python dependencies
└── .agents/skills/torrent_search/
    └── SKILL.md           # This file
```

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install fzf

```bash
# Windows (winget)
winget install junegunn.fzf

# macOS (Homebrew)
brew install fzf

# Linux (apt)
sudo apt install fzf
```

### 3. Ensure a torrent client is installed

The app opens magnet links using the system default handler. Install a client like [qBittorrent](https://www.qbittorrent.org/) and set it as the default handler for magnet links.

## Usage

### Interactive mode

```bash
python torrent_search.py
```

### Direct query

```bash
python torrent_search.py -q "Interstellar"
```

### Windows shortcut

```bash
torrent.bat "Interstellar"
```

## How It Works

1. User enters a search query
2. The app queries `https://apibay.org/q.php?q=<query>`
3. Results are displayed in a rich table with Name, Size, Seeds, and Leeches
4. `fzf` opens for interactive fuzzy selection (falls back to manual input if fzf is unavailable)
5. A magnet link is built from the selected torrent's `info_hash` and opened with the system default torrent client

## Configuration

| Constant       | Default | Description                          |
|----------------|---------|--------------------------------------|
| `API_URL`      | apibay  | Base API endpoint for torrent search |
| `MAX_RESULTS`  | 20      | Maximum results to display           |
| `TRACKERS`     | 8 URLs  | Tracker list appended to magnet URIs |

## Troubleshooting

| Problem                          | Solution                                                      |
|----------------------------------|---------------------------------------------------------------|
| `fzf not found`                  | Install fzf or restart your shell after installation          |
| API request fails                | Check internet connection; API may be blocked by ISP (use VPN)|
| Magnet link doesn't open         | Set qBittorrent as default handler for `magnet:` links        |
| `No results found`               | Try a different or broader search term                        |
