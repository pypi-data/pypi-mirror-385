"""Functions for computing total solvency capital requirements.

This module provides functionality to calculate the total solvency capital requirement (SCR),
which is the sum of junior and senior SCR, for active insurance policies at specific points
in time and over time series.
"""

import pandas as pd

from ensuro_analytics.analytics.base import active_at_t, constants, today
from ensuro_analytics.analytics.portfolio.base import _max_date_range, date_to_period

REQUIRED_COLUMNS = ["sr_scr", "jr_scr", "expired_on", "start", "expiration"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """Compute the current value of total solvency capital.

    Args:
        data: DataFrame containing policy data.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of junior and senior solvency capital for currently active policies.
    """
    mask = active_at_t(data, today())
    return data.loc[mask].jr_scr.sum() + data.loc[mask].sr_scr.sum()


def at_t(data: pd.DataFrame, date: pd.Timestamp, **kwargs) -> float:
    """Compute the total solvency capital at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the total capital.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of junior and senior solvency capital for policies active at the given date.
    """
    mask = active_at_t(data, date)
    return data.loc[mask].sr_scr.sum() + data.loc[mask].jr_scr.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of total solvency capital values.

    Args:
        data: DataFrame containing policy data.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "start",
            "expiration", "expired_on", or "max". Defaults to "start".
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing total solvency capital values indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "sr_scr" in data.columns, "sr_scr column is required"
    assert "jr_scr" in data.columns, "jr_scr column is required"
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "start" in data.columns, "start column is required"

    if period_column == "max":
        dates = _max_date_range(data=data, freq=freq)
    else:
        dates = sorted(date_to_period(dates=data[period_column], freq=freq).unique())

    scr = []

    def get_data() -> pd.DataFrame:
        """Get a copy of the relevant data columns.

        Returns:
            A DataFrame containing only the start, expired_on, sr_scr, and jr_scr columns.
        """
        return data[["start", "expired_on", "sr_scr", "jr_scr"]].copy()

    for date in dates:
        scr.append(at_t(get_data(), date))

    scr = pd.Series(scr, index=dates, name="scr")

    if start_date is not None:
        scr = scr.loc[scr.index >= start_date]
    if end_date is not None:
        scr = scr.loc[scr.index <= end_date]

    return scr
