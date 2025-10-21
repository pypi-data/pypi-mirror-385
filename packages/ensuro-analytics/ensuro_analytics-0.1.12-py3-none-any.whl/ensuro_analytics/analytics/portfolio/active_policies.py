"""Functions for computing and analyzing active insurance policies.

This module provides functionality to calculate the number of active policies
at specific points in time and over time series.
"""

import pandas as pd

from ensuro_analytics.analytics.base import active_at_t, constants, today
from ensuro_analytics.analytics.portfolio.base import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["start", "expired_on", "expiration"]


def current_value(data: pd.DataFrame, **kwargs) -> int:
    """Compute the number of currently active policies.

    Args:
        data: DataFrame containing policy data.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The number of active policies at the current date.
    """
    mask = active_at_t(data, today())
    return mask.astype(int).sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> int:
    """Compute the number of active policies at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to count active policies.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The number of active policies at the given date.
    """
    mask = active_at_t(data, date)
    return mask.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of active policy counts.

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
        A Series containing active policy counts indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    # Get unique dates at a regular interval
    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    active_policies = []

    def get_data():
        """Get a copy of the relevant data columns.

        Returns:
            A DataFrame containing only the start and expired_on columns.
        """
        return data[["start", "expired_on"]].copy()

    # Compute active policies at each date
    for date in dates:
        active_policies.append(at_t(get_data(), date))

    active_policies = pd.Series(active_policies, index=dates, name="active_policies")

    # Filter by start and end date
    if start_date is not None:
        active_policies = active_policies.loc[active_policies.index >= start_date]
    if end_date is not None:
        active_policies = active_policies.loc[active_policies.index <= end_date]

    return active_policies
