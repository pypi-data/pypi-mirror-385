"""Functions for computing insurance policy payout counts.

This module provides functionality to calculate the number of insurance policies that
resulted in payouts at specific points in time and over time series, with options for
post-mortem analysis and cumulative counting.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import _count_payouts, constants, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "start", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> int:
    """Compute the current total number of payouts.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, only count payouts for policies with expiration
            date <= today. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The total number of policies that resulted in payouts.
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]

    n_payouts = (_data.actual_payout > 1e-9).sum()

    return n_payouts


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> int:
    """Compute the number of payouts at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to count payouts.
        post_mortem: If True, only count payouts for policies with expiration
            date <= date. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The number of policies that resulted in payouts at the given date.
    """
    if post_mortem is True:
        mask = (data.expiration <= date) & data.actual_payout.notna() & data.expired_on.notna()
    else:
        mask = np.ones(len(data), dtype=bool)

    mask &= data.start <= date
    return (data.loc[mask].actual_payout > 1e-9).sum()


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of payout counts.

    Policies are divided into batches based on their expected expiration date.
    For each batch, the function computes the number of payouts. If cumulative
    is True, the counts are cumulative over time.

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute cumulative payout counts over time.
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
        A Series containing payout counts indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert "start" in data.columns, "start column is required"
    assert "expired_on" in data.columns, "expired_on column is required"

    _data = data.copy()

    # Find first day of expiration week
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)

    _data = (
        _data.groupby("date")
        .agg({"actual_payout": _count_payouts})
        .rename(columns={"actual_payout": "n_payout"})
    )

    if cumulative:
        _data["n_payout"] = _data.n_payout.cumsum()

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["n_payout"]
