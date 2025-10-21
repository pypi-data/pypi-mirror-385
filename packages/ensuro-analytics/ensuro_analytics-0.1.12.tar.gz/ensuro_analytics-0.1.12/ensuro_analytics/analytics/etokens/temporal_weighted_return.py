"""Functions for computing temporally weighted yearly returns.

This module provides functionality to calculate temporally weighted yearly returns for eTokens,
which accounts for the time-weighted nature of returns over different periods. It supports:
- Current value calculations
- Historical value calculations at specific dates
- Time series generation with configurable frequency
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.etokens.base import TimeUnits

REQUIRED_COLUMNS = ["returns", "perfect_returns"]


def current_value(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    **kwargs,
) -> float:
    """Compute the current temporally weighted yearly return.

    This function calculates the annualized return using a time-weighted approach,
    which accounts for the duration of the investment period. The calculation
    considers either nominal returns or perfect returns based on the full_ur parameter.

    Args:
        data: DataFrame containing eToken returns data with a multi-index of eToken and date.
        full_ur: Whether to use perfect returns (full unrealized returns) instead of
            nominal returns. Defaults to False.
        time_resolution: Time resolution for the return calculation. Can be a string
            (e.g., "1D") or TimeUnits object. Defaults to "1D" (daily).
        **kwargs: Additional keyword arguments (not used).

    Returns:
        The temporally weighted yearly return as a decimal (e.g., 0.15 for 15%).

    Raises:
        AssertionError: If there are repeated dates in the data.
    """
    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    # Check if there are repeated dates
    assert data.index.get_level_values("date").nunique() == len(
        data.index.get_level_values("date")
    ), "There are repeated dates"

    if full_ur:
        col = "perfect_returns"
    else:
        col = "returns"

    data = data[data[col].notnull()]

    if len(data) == 0:
        return np.nan

    # Compute the total number of days in the time series
    n_days = (
        data.index.get_level_values("date").max() - data.index.get_level_values("date").min()
    ).days + time_resolution.n_days_in_unit

    # Compute the total return of the time series
    ret = (data[col] + 1).prod() - 1

    # Compute the APY
    time_weighted_yearly_return = (1 + ret) ** (365 / n_days) - 1

    return time_weighted_yearly_return


def at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    **kwargs,
) -> float:
    """Compute the temporally weighted yearly return at a specific date.

    This function calculates the annualized return using a time-weighted approach
    up to a specified date, considering either nominal returns or perfect returns.

    Args:
        data: DataFrame containing eToken returns data with a multi-index of eToken and date.
        date: The date at which to compute the return. Must be after the minimum date
            plus the time resolution period.
        full_ur: Whether to use perfect returns (full unrealized returns) instead of
            nominal returns. Defaults to False.
        time_resolution: Time resolution for the return calculation. Can be a string
            (e.g., "1D") or TimeUnits object. Defaults to "1D" (daily).
        **kwargs: Additional keyword arguments (not used).

    Returns:
        The temporally weighted yearly return at the given date as a decimal.

    Raises:
        AssertionError: If the specified date is too early (before minimum date plus
            time resolution period).
    """
    if date.tz is None:
        date = date.tz_localize("UTC")

    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    assert date > data.index.get_level_values("date").min() + pd.Timedelta(
        f"{time_resolution.n_days_in_unit}D"
    ), "Date is too early"

    mask = data.index.get_level_values("date") < date

    return current_value(data[mask].copy(), full_ur=full_ur, time_resolution=time_resolution)


def time_series(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    **kwargs,
) -> pd.Series:
    """Compute the temporally weighted yearly return time series.

    This function generates a time series of annualized returns using a time-weighted
    approach, with configurable frequency and date range. The calculation considers
    either nominal returns or perfect returns based on the full_ur parameter.

    Args:
        data: DataFrame containing eToken returns data with a multi-index of eToken and date.
        full_ur: Whether to use perfect returns (full unrealized returns) instead of
            nominal returns. Defaults to False.
        time_resolution: Time resolution for the return calculation. Can be a string
            (e.g., "1D") or TimeUnits object. Defaults to "1D" (daily).
        freq: Frequency for the time series. Defaults to "1W" (weekly).
        end_date: Maximum date for the time series. If None, uses today's date.
        start_date: Minimum date for the time series. If None, uses 90 days before today.
        **kwargs: Additional keyword arguments (not used).

    Returns:
        A Series containing the temporally weighted yearly returns indexed by date.

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

    ts = pd.Series(
        index=ts_dates,
        data=[at_t(data, date, full_ur=full_ur, time_resolution=time_resolution) for date in ts_dates],
    )

    return ts
