"""Functions for computing the beta of eToken returns.

This module provides functionality to calculate the beta (market sensitivity) of eToken
returns relative to the market benchmark, with options for different time resolutions
and full unrealized returns analysis.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.etokens.base import TimeUnits, get_market_returns

REQUIRED_COLUMNS = ["returns", "perfect_returns"]


def current_value(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    **kwargs,
) -> float:
    """Compute the current Beta of eToken returns.

    Beta measures the sensitivity of an investment's returns to market movements.
    A beta of 1 indicates the investment moves in line with the market, while a beta
    greater than 1 indicates higher volatility than the market.

    Args:
        data: DataFrame containing eToken returns data with a multi-index including dates.
        full_ur: If True, use perfect returns (including unrealized returns) instead of
            realized returns. Defaults to False.
        time_resolution: Time resolution for computing returns. Can be a string (e.g., "1D")
            or TimeUnits object. Defaults to "1D" (daily).
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The Beta value, representing the market sensitivity of the returns.

    Raises:
        AssertionError: If there are repeated dates in the data.
    """
    # if isinstance(time_resolution, str):
    #     time_resolution = TimeUnits(time_resolution)

    # Check if there are repeated dates
    assert data.index.get_level_values("date").nunique() == len(
        data.index.get_level_values("date")
    ), "There are repeated dates"

    market_data = get_market_returns(dates=data.index.get_level_values("date"))

    if full_ur:
        col = "perfect_returns"
    else:
        col = "returns"

    returns_with_benchmarks = (
        pd.merge(market_data[["date", "returns_sp"]], data.reset_index()[["date", col]])
        .dropna()
        .set_index("date")
    )

    returns_with_benchmarks = returns_with_benchmarks[returns_with_benchmarks.notnull()]

    if len(returns_with_benchmarks) == 0:
        return np.nan

    covariance_matrix = returns_with_benchmarks[[col, "returns_sp"]].cov()
    beta = covariance_matrix.loc[col, "returns_sp"] / covariance_matrix.loc["returns_sp", "returns_sp"]

    return beta


def at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    **kwargs,
) -> float:
    """Compute the Beta at a specific point in time.

    Args:
        data: DataFrame containing eToken returns data with a multi-index including dates.
        date: The timestamp at which to compute the Beta.
        full_ur: If True, use perfect returns (including unrealized returns) instead of
            realized returns. Defaults to False.
        time_resolution: Time resolution for computing returns. Can be a string (e.g., "1D")
            or TimeUnits object. Defaults to "1D" (daily).
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The Beta value at the given date.

    Raises:
        AssertionError: If the date is too early relative to the data and time resolution.
    """
    if date.tz is None:
        date = date.tz_localize("UTC")

    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    assert date > data.index.get_level_values("date").min() + pd.Timedelta(
        f"{time_resolution.n_days_in_unit}D"
    ), "Date is too early"

    mask = data.index.get_level_values("date") < date
    return current_value(data.loc[mask], full_ur, time_resolution, **kwargs)


def time_series(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    **kwargs,
) -> pd.Series:
    """Compute a time series of Beta values.

    Args:
        data: DataFrame containing eToken returns data with a multi-index including dates.
        full_ur: If True, use perfect returns (including unrealized returns) instead of
            realized returns. Defaults to False.
        time_resolution: Time resolution for computing returns. Can be a string (e.g., "1D")
            or TimeUnits object. Defaults to "1D" (daily).
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use today.
        start_date: Minimum date to include. If None, use 90 days before today.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing Beta values indexed by date.
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

    ts = pd.Series(
        index=ts_dates,
        data=[at_t(data, date, full_ur=full_ur, time_resolution=time_resolution) for date in ts_dates],
    )

    return ts
