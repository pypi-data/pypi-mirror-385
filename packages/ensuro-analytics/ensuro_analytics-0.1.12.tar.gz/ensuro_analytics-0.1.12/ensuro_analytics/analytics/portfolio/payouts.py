"""Functions for computing insurance policy payouts.

This module provides functionality to calculate the total value of payouts made for
insurance policies at specific points in time and over time series, with options for
post-mortem analysis and cumulative calculations.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """Compute the current total value of payouts.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, only include payouts for policies with expiration
            date <= today. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of all payouts that meet the criteria.
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]

    payouts = _data.actual_payout.sum()

    return payouts


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """Compute the total value of payouts at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute payouts.
        post_mortem: If True, only include payouts for policies with expiration
            date <= date. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of all payouts that meet the criteria at the given date.
    """
    if post_mortem is True:
        mask = (data.expiration <= date) & data.actual_payout.notna() & data.expired_on.notna()
    else:
        mask = np.ones(len(data), dtype=bool)
    mask &= data.expired_on <= date
    return np.nansum(data.loc[mask].actual_payout.values)


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of payout values.

    Policies are divided into batches based on their expected expiration date.
    For each batch, the function computes the total payouts. If cumulative is True,
    the values represent cumulative payouts over time.

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute cumulative payout values over time.
            Defaults to False.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "start",
            "expired_on", or "expiration". Defaults to "expiration".
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing payout values indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "expiration" in data.columns, "expiration column is required"
    assert "expired_on" in data.columns, "expired_on column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"

    _data = data.copy()

    # Transform dates into regular intervals
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)
    _data = _data.groupby("date").agg({"actual_payout": "sum"})

    if cumulative:
        _data["actual_payout"] = _data.actual_payout.cumsum()

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["actual_payout"]
