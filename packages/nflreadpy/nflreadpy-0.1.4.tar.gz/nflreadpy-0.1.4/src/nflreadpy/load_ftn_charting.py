"""Load FTN charting data."""

import polars as pl

from .downloader import get_downloader
from .utils_date import get_current_season


def load_ftn_charting(seasons: int | list[int] | bool | None = None) -> pl.DataFrame:
    """
    Load FTN charting data.

    Data available since 2022.

    Args:
        seasons: Season(s) to load. If None, loads current season.
                If True, loads all available data since 2022.
                If int or list of ints, loads specified season(s).

    Returns:
        Polars DataFrame with FTN charting data including detailed\
        play-by-play charting information and advanced metrics.

    See Also:
        <https://nflreadr.nflverse.com/reference/load_ftn_charting.html>

    Data Dictionary:
        <https://nflreadr.nflverse.com/articles/dictionary_ftn_charting.html>
    """
    if seasons is None:
        seasons = [get_current_season()]
    elif seasons is True:
        # Load all available seasons (2022 to current)
        current_season = get_current_season()
        seasons = list(range(2022, current_season + 1))
    elif isinstance(seasons, int):
        seasons = [seasons]

    # Validate seasons
    current_season = get_current_season()
    for season in seasons:
        if not isinstance(season, int) or season < 2022 or season > current_season:
            raise ValueError(f"Season must be between 2022 and {current_season}")

    downloader = get_downloader()
    dataframes = []

    for season in seasons:
        path = f"ftn_charting/ftn_charting_{season}"
        df = downloader.download("nflverse-data", path, season=season)
        dataframes.append(df)

    if len(dataframes) == 1:
        return dataframes[0]
    else:
        return pl.concat(dataframes, how="diagonal_relaxed")
