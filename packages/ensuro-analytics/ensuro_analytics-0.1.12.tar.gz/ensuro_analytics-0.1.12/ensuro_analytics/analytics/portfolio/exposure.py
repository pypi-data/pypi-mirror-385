"""Functions for computing insurance policy exposure.

This module provides functionality to calculate the total exposure (sum of potential payouts)
for active insurance policies at specific points in time and over time series.
"""

import pandas as pd

from ensuro_analytics.analytics.base import active_at_t, constants, today
from ensuro_analytics.analytics.portfolio.base import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["payout", "start", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """Compute the current total exposure of active policies.

    Args:
        data: DataFrame containing policy data.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of potential payouts for all currently active policies.
    """
    mask = active_at_t(data, today())
    return data.loc[mask].payout.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """Compute the total exposure at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the exposure.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of potential payouts for all policies active at the given date.
    """
    mask = active_at_t(data, date)
    return data.loc[mask].payout.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of total exposure values.

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
        A Series containing total exposure values indexed by date.

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

    exposure = []

    def get_data() -> pd.DataFrame:
        """Get a copy of the relevant data columns.

        Returns:
            A DataFrame containing only the start, expired_on, and payout columns.
        """
        return data[["start", "expired_on", "payout"]].copy()

    # Compute active policies at each date
    for date in dates:
        exposure.append(at_t(get_data(), date))

    exposure = pd.Series(exposure, index=dates, name="exposure")

    # Filter by start and end date
    if start_date is not None:
        exposure = exposure.loc[exposure.index >= start_date]
    if end_date is not None:
        exposure = exposure.loc[exposure.index <= end_date]

    return exposure
