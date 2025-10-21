"""Functions for computing collected insurance premiums.

This module provides functionality to calculate the total value of premiums collected
from expired insurance policies at specific points in time and over time series.
"""

import pandas as pd

from ensuro_analytics.analytics.base import active_at_t, constants, today
from ensuro_analytics.analytics.portfolio.base import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["premium", "start", "expired_on"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """Compute the current value of collected premiums.

    Args:
        data: DataFrame containing policy data.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums from all expired (inactive) policies.
    """
    mask = active_at_t(data, today())
    return data.loc[~mask].premium.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """Compute the value of collected premiums at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute collected premiums.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums from policies that expired before the given date.
    """
    mask = (~data.expired_on.isna()) & (data.expired_on < date)
    return data.loc[mask].premium.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of collected premium values.

    For each time period, calculates the total value of premiums from policies
    that have expired ("won" premiums).

    Args:
        data: DataFrame containing policy data.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "start",
            "expired_on", "expiration", or "max". Defaults to "start".
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing collected premium values indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "premium" in data.columns, "premium column is required"
    assert period_column in data.columns, f"{period_column} column is required"
    assert "expired_on" in data.columns, "expired_on column is required"

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    inactive_premiums = []

    def get_data():
        return data[["expired_on", "premium"]].copy()

    for date in dates:
        inactive_premiums.append(at_t(get_data(), date))

    inactive_premiums = pd.Series(inactive_premiums, index=dates, name="collected_premiums")

    if start_date is not None:
        inactive_premiums = inactive_premiums.loc[inactive_premiums.index >= start_date]
    if end_date is not None:
        inactive_premiums = inactive_premiums.loc[inactive_premiums.index <= end_date]

    return inactive_premiums


def rolling_at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    timedelta: pd.Timedelta = pd.Timedelta(days=7),
    **kwargs,
) -> float:
    """Compute the value of collected premiums within a time window.

    Args:
        data: DataFrame containing policy data.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of pure premiums from policies that expired within the specified
        time window.
    """
    data = data.loc[~data.expired_on.isna()]
    mask = (data.expired_on > date - timedelta) & (data.expired_on <= date + timedelta)
    return data.loc[mask].premium.sum()
