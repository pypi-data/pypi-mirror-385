# PyTorrentSearch

CLI + Python library to search for and parse magnet links from the Internet.

It leverages well known search engines such as Yandex, Google and DuckDuckGo. In my tests only Google was able to work reliably.

If you already have the website link you can just paste it as it would be a query then it will look for all magnet links that it can find in the raw HTML.

The idea is to quickly classify good sites and bad sites based on if the magnet link is already in the base HTML without having to load the JavaScript crap.

**DISCLAIMER**: Use at your own risk. This software doesn't store or provide illegal content by itself, it's only a search tool.

## Installation & Usage

Run directly without installation using `uvx`:

```bash
uvx pytorrentsearch "your search query"
```

Or install globally:

```bash
uv tool install pytorrentsearch
pytorrentsearch "your search query"
```

You can also provide a direct URL to parse:

```bash
uvx pytorrentsearch "https://example.com/torrent-page"
```

## Development

This project uses [mise](https://mise.jdx.dev/) for tool management and [uv](https://docs.astral.sh/uv/) for Python dependency management.

### Setup

```bash
# Install mise (if not already installed)
# See: https://mise.jdx.dev/getting-started.html

# Install tools (uv, ruff)
mise install

# Install Python dependencies
uv sync
```

### Available Commands

```bash
# Format code
mise run fmt

# Run linter
mise run lint

# Run tests
mise run test

# Build package
mise run build

# Clean build artifacts
mise run clean
```
