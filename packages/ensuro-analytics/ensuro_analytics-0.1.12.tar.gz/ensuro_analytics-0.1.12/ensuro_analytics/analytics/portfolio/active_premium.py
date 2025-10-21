"""Functions for computing and analyzing premiums of active insurance policies.

This module provides functionality to calculate premium values for active policies
at specific points in time and over time series.
"""

import pandas as pd

from ensuro_analytics.analytics.base import active_at_t, constants, today
from ensuro_analytics.analytics.portfolio.base import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["premium", "expired_on", "start"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """Compute the total premium value of currently active policies.

    Args:
        data: DataFrame containing policy data.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums for all currently active policies.
    """
    mask = active_at_t(data, today())
    return data.loc[mask].premium.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """Compute the total premium value of active policies at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute active premiums.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums for all policies active at the given date.
    """
    mask = active_at_t(data, date)
    return data.loc[mask].premium.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of active premium values.

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
        A Series containing active premium values indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "premium" in data.columns, "premium column is required"
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    active_premiums = []

    def get_data():
        """Get a copy of the relevant data columns.

        Returns:
            A DataFrame containing only the start, expired_on, and premium columns.
        """
        return data[["start", "expired_on", "premium"]].copy()

    for date in dates:
        active_premiums.append(at_t(get_data(), date))

    active_premiums = pd.Series(active_premiums, index=dates, name="active_premiums")

    if start_date is not None:
        active_premiums = active_premiums.loc[active_premiums.index >= start_date]
    if end_date is not None:
        active_premiums = active_premiums.loc[active_premiums.index <= end_date]

    return active_premiums
