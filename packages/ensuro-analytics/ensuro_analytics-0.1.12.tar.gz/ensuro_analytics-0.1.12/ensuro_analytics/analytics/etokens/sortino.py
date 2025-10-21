"""Functions for computing the Sortino ratio of eToken returns.

This module provides functionality to calculate the Sortino ratio (downside risk-adjusted return)
of eToken returns relative to the risk-free rate, with options for different time
resolutions and full unrealized returns analysis.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.etokens.base import TimeUnits, risk_free_rate

REQUIRED_COLUMNS = ["returns", "perfect_returns"]


def current_value(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    **kwargs,
) -> float:
    """Compute the current Sortino ratio of eToken returns.

    The Sortino ratio measures the excess return per unit of downside risk (volatility
    of negative returns) of an investment relative to the risk-free rate. A higher
    Sortino ratio indicates better risk-adjusted performance, focusing only on downside
    volatility.

    Args:
        data: DataFrame containing eToken returns data with a multi-index including dates.
        full_ur: If True, use perfect returns (including unrealized returns) instead of
            realized returns. Defaults to False.
        time_resolution: Time resolution for computing returns. Can be a string (e.g., "1D")
            or TimeUnits object. Defaults to "1D" (daily).
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The Sortino ratio value, representing the downside risk-adjusted return.

    Raises:
        AssertionError: If there are repeated dates in the data.
    """
    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    # Check if there are repeated dates
    assert data.index.get_level_values("date").nunique() == len(
        data.index.get_level_values("date")
    ), "There are repeated dates"

    last_date = data.index.get_level_values("date").max()
    rf_rate = risk_free_rate(end_date=last_date, start_date=last_date - 365 * constants.day)

    if full_ur:
        col = "perfect_returns"
    else:
        col = "returns"

    data = data[data[col].notnull()]

    if len(data) == 0:
        return np.nan

    # Compute the number of units in one year based on the time resolution
    yearly_units = time_resolution.n_units_in_one_year

    # Compute the reference rate
    ref_r = (1 + rf_rate) ** (1 / yearly_units) - 1

    # Compute the Sortino ratio
    residuals = ref_r - data[data[col] - ref_r < 0][col]
    ddev = np.sqrt((residuals**2).sum() / len(data))
    sortino = (data[col].mean() - ref_r) / ddev

    return sortino


def at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    **kwargs,
) -> float:
    """Compute the Sortino ratio at a specific point in time.

    Args:
        data: DataFrame containing eToken returns data with a multi-index including dates.
        date: The timestamp at which to compute the Sortino ratio.
        full_ur: If True, use perfect returns (including unrealized returns) instead of
            realized returns. Defaults to False.
        time_resolution: Time resolution for computing returns. Can be a string (e.g., "1D")
            or TimeUnits object. Defaults to "1D" (daily).
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The Sortino ratio value at the given date.

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
    """Compute a time series of Sortino ratio values.

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
        A Series containing Sortino ratio values indexed by date.
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
