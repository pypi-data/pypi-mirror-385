"""Functions for computing total insurance policy counts.

This module provides functionality to calculate the total number of policies sold
at specific points in time and over time series, with options for post-mortem analysis
and cumulative counting.
"""

import pandas as pd

from ensuro_analytics.analytics.base import _timestamp, constants, started_between, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = ["expiration", "start", "pure_premium", "premium", "expired_on", "actual_payout"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> int:
    """Compute the current total number of policies sold.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, only count policies with expiration date <= today.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The total number of policies sold that meet the criteria.
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]

    return _data.shape[0]


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> int:
    """Compute the total number of policies sold at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to count policies.
        post_mortem: If True, only count policies with expiration date <= date.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The total number of policies sold that meet the criteria at the given date.
    """
    mask = data.start <= _timestamp(date)
    if post_mortem:
        mask &= data.expiration <= _timestamp(date)
    return mask.sum()


def time_series(
    data: pd.DataFrame,
    freq: str = "1W",
    cumulative: bool = False,
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of total policy counts.

    Policies are divided into batches based on their start date. For each batch,
    the function computes the number of policies sold. If cumulative is True,
    the counts are cumulative over time.

    Args:
        data: DataFrame containing policy data.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        cumulative: If True, compute cumulative policy counts over time.
            Defaults to False.
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "start",
            "expired_on", or "expiration". Defaults to "start".
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing policy counts indexed by date.
    """
    _data = data.copy()
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)
    _data = (
        _data.groupby("date")
        .agg({"pure_premium": "count"})
        .rename(columns={"pure_premium": "total_policies"})
    )

    if cumulative is True:
        _data["total_policies"] = _data["total_policies"].cumsum()

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["total_policies"]


def rolling_at_t(
    data: pd.DataFrame, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
) -> int:
    """Compute the number of policies sold within a time window.

    Args:
        data: DataFrame containing policy data.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The number of policies sold within the specified time window.
    """
    start_date = date - timedelta
    end_date = date + timedelta
    mask = started_between(data, start_date=start_date, end_date=end_date)
    return mask.sum()
