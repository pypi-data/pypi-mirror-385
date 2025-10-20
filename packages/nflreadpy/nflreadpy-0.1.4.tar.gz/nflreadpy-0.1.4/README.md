# nflreadpy <a href='https://nflreadpy.nflverse.com'><img src='docs/assets/nflverse.png' align="right" width="25%" min-width="120px" /></a>
<!-- badges: start -->
[![PyPI status](https://img.shields.io/pypi/v/nflreadpy?style=flat-square&logo=python&label=pypi)](https://pypi.org/project/nflreadpy/)
[![Dev status](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fgithub.com%2Fnflverse%2Fnflreadpy%2Fraw%2Fmain%2Fpyproject.toml&query=%24.project.version&prefix=v&style=flat-square&label=dev%20version
)](https://nflreadpy.nflverse.com/)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg?style=flat-square)](https://lifecycle.r-lib.org/articles/stages.html)
[![CI test status](https://img.shields.io/github/actions/workflow/status/nflverse/nflreadpy/ci-test.yaml?label=CI%20tests&style=flat-square&logo=github)](https://github.com/nflverse/nflreadpy/actions)
[![nflverse discord](https://img.shields.io/discord/789805604076126219?color=7289da&label=nflverse%20discord&logo=discord&logoColor=fff&style=flat-square)](https://discord.com/invite/5Er2FBnnQa)

<!-- badges: end -->

A Python package for downloading NFL data from nflverse repositories. This is a
Python port of the popular R package [nflreadr](https://github.com/nflverse/nflreadr),
designed to provide easy access to NFL data with caching, progress tracking, and
modern Python conventions.

## Features

- Compatible API with nflreadr R package
- Fast data loading with Polars DataFrames
- Intelligent caching (memory or filesystem)
- Progress tracking for large downloads

## Install

```bash
# Using uv (recommended)
uv add nflreadpy

# Using pip
pip install nflreadpy
```

## Usage

```python
import nflreadpy as nfl

# Load current season play-by-play data
pbp = nfl.load_pbp()

# Load player game-level stats for multiple seasons
player_stats = nfl.load_player_stats([2022, 2023])

# Load all available team level stats
team_stats = nfl.load_team_stats(seasons=True)

# nflreadpy uses Polars instead of pandas. Convert to pandas if needed:
pbp_pandas = pbp.to_pandas()
```

## Available Functions

### Core Loading Functions

- `load_pbp()` - play-by-play data
- `load_player_stats()` - player game or season statistics
- `load_team_stats()` - team game or season statistics
- `load_schedules()` - game schedules and results
- `load_players()` - player information
- `load_rosters()` - team rosters
- `load_rosters_weekly()` - team rosters by season-week
- `load_snap_counts()` - snap counts
- `load_nextgen_stats()` - advanced stats from nextgenstats.nfl.com
- `load_ftn_charting()` - charted stats from ftnfantasy.com/data
- `load_participation()` - participation data (historical)
- `load_draft_picks()` - nfl draft picks
- `load_injuries()` - injury statuses and practice participation
- `load_contracts()` - historical contract data from OTC
- `load_officials()` - officials for each game
- `load_combine()` - nfl combine results
- `load_depth_charts()` - depth charts
- `load_trades()` - trades
- `load_ff_playerids()` - ffverse/dynastyprocess player ids
- `load_ff_rankings()` - fantasypros rankings
- `load_ff_opportunity()` - expected yards, touchdowns, and fantasy points

### Utility Functions

- `clear_cache()` - Clear cached data
- `get_current_season()` - Get current NFL season
- `get_current_week()` - Get current NFL week

## Configuration

Configure nflreadpy using environment variables:

```bash
export NFLREADPY_CACHE='memory' # Cache mode ("memory", "filesystem", or "off")
export NFLREADPY_CACHE_DIR='~/my_cache_dir' # Directory path for filesystem cache
export NFLREADPY_CACHE_DURATION=86400 # Cache duration in seconds

export NFLREADPY_VERBOSE='False' # Enable verbose output (true/false)
export NFLREADPY_TIMEOUT=30 # HTTP request timeout in seconds
export NFLREADPY_USER_AGENT='nflreadpy/v0.1.1' # Custom user agent string
```

or configure programmatically:

```python
from nflreadpy.config import update_config

update_config(
    cache_mode="memory",
    cache_dir='~/my_cache_dir',
    cache_duration=86400,
    verbose=False,
    timeout=30,
    user_agent='nflreadpy/v0.1.1'
)
```

## Getting help

The best places to get help on this package are:

- the [nflverse discord](https://discord.com/invite/5Er2FBnnQa) (for
  both this package as well as anything NFL analytics related)
- opening [an issue](https://github.com/nflverse/nflreadpy/issues/new/choose)

## Data Sources

nflreadpy downloads data from the following nflverse repositories:

- [nflverse-data](https://github.com/nflverse/nflverse-data) - Play-by-play, rosters, stats
- [dynastyprocess](https://github.com/dynastyprocess/data) - fantasy football data
- [ffopportunity](https://github.com/ffverse/ffopportunity) - expected yards and fantasy points

See the automation status page [here](https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html)
for last update date/times for each release.

## License

MIT License - see [LICENSE](LICENSE) file for details.

The majority of all nflverse data available (ie all but the FTN data as of July 2025)
is broadly licensed as CC-BY 4.0, and the FTN data is CC-BY-SA 4.0 (see nflreadr
docs for each main data file).

## Development

This project uses the following tooling:

- uv for dependency management
- ruff for linting and formatting
- mypy for type checking
- pytest for testing
- mkdocs for documentation site

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run ruff format

# Type check
uv run mypy src

# Serve docs site locally
uv run mkdocs serve

# Build docs site
uv run mkdocs build
```

## Disclaimer
Most of the first version was written by Claude based on nflreadr, use at your
own risk.

## Contributing

Many hands make light work! Here are some ways you can contribute to
this project:

- You can [open an issue](https://github.com/nflverse/nflreadpy/issues/new/choose) if
you’d like to request a feature or report a bug/error.

- If you’d like to contribute code, please check out [the contribution guidelines](CONTRIBUTING.md).
