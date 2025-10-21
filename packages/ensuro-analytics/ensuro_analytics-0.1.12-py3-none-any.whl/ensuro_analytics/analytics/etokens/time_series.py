"""Utilities for generating time series data from eToken metrics.

This module provides functionality to create time series data from eToken metrics,
including:
- Daily returns calculation
- Time series generation with configurable frequency
- Data normalization and transformation
"""

import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.etokens.base import TimeUnits


def daily_returns(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
) -> pd.DataFrame:
    """Calculate daily returns from eToken metrics.

    This function computes daily returns by considering:
    - Total supply changes
    - Deposit and withdrawal flows
    - Dividend calculations
    - Proper date handling and normalization

    Args:
        data: DataFrame containing eToken metrics with a multi-index of eToken and date.
        full_ur: Whether to use perfect returns (full unrealized returns) instead of
            nominal returns. Defaults to False.
        time_resolution: Time resolution for the return calculation. Can be a string
            (e.g., "1D") or TimeUnits object. Defaults to "1D" (daily).

    Returns:
        A DataFrame containing daily returns with a multi-index of eToken and date.
    """
    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    # Check if there are repeated dates
    assert data.index.get_level_values("date").nunique() == len(
        data.index.get_level_values("date")
    ), "There are repeated dates"

    # Compute daily returns
    daily_returns = pd.DataFrame(index=data.index, columns=["returns"])
    daily_returns["returns"] = data.groupby(level="e_token").total_supply.pct_change()

    # Compute perfect returns (full unrealized returns)
    daily_returns["perfect_returns"] = daily_returns["returns"].copy()
    daily_returns.loc[daily_returns["perfect_returns"].isnull(), "perfect_returns"] = 0

    # Add dividend returns
    daily_returns["returns"] += data["dividend"] / data["total_supply"]
    daily_returns["perfect_returns"] += data["dividend"] / data["total_supply"]

    # Add insurance returns
    daily_returns["returns"] += data["dividend_insurance"]
    daily_returns["perfect_returns"] += data["dividend_insurance"]

    return daily_returns


def time_series(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
) -> pd.Series:
    """Generate a time series of eToken returns.

    This function creates a time series of returns with configurable frequency and
    date range, considering either nominal returns or perfect returns.

    Args:
        data: DataFrame containing eToken metrics with a multi-index of eToken and date.
        full_ur: Whether to use perfect returns (full unrealized returns) instead of
            nominal returns. Defaults to False.
        time_resolution: Time resolution for the return calculation. Can be a string
            (e.g., "1D") or TimeUnits object. Defaults to "1D" (daily).
        freq: Frequency for the time series. Defaults to "1W" (weekly).
        end_date: Maximum date for the time series. If None, uses today's date.
        start_date: Minimum date for the time series. If None, uses 90 days before today.

    Returns:
        A Series containing the returns indexed by date.

    Note:
        The start date is adjusted to ensure sufficient data for the first calculation,
        considering both the frequency and time resolution parameters.
    """
    # Localize the dates as UTC if they are not localized
    if start_date.tz is None:
        start_date = start_date.tz_localize("UTC")

    if end_date.tz is None:
        end_date = end_date.tz_localize("UTC")

    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    freq_unit = TimeUnits("1" + freq[-1])
    freq_days = int(freq[:-1]) * freq_unit.n_days_in_unit

    start_date = max(
        start_date,
        data.index.get_level_values("date").min() + pd.Timedelta(f"{freq_days}D"),
        data.index.get_level_values("date").min() + pd.Timedelta(f"{time_resolution.n_days_in_unit}D"),
    )

    ts_dates = pd.date_range(start=start_date, end=end_date, freq=freq, tz="UTC")

    # Compute daily returns
    daily_returns_df = daily_returns(data, full_ur=full_ur, time_resolution=time_resolution)

    # Compute time series
    ts = pd.Series(
        index=ts_dates,
        data=[
            daily_returns_df.loc[daily_returns_df.index.get_level_values("date") < date, "returns"].mean()
            for date in ts_dates
        ],
    )

    return ts
