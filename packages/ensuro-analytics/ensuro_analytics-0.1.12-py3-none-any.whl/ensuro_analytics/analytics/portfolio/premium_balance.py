"""Functions for computing insurance premium balances.

This module provides functionality to calculate the balance between premiums collected
and payouts made for insurance policies at specific points in time and over time series,
with options for post-mortem analysis and using pure premiums.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = [
    "premium",
    "pure_premium",
    "actual_payout",
    "expiration",
    "expired_on",
    "start",
]


def current_value(
    data: pd.DataFrame,
    post_mortem: bool = False,
    use_pure_premium: bool = True,
    **kwargs,
) -> float:
    """Compute the current premium balance.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, only include policies with expiration date <= today.
            Defaults to False.
        use_pure_premium: If True, use pure premium instead of total premium.
            Defaults to True.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The difference between total premiums and actual payouts.
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]
    premium_column = "pure_premium" if use_pure_premium else "premium"
    premium_balance = _data.loc[:, premium_column].sum() - np.nansum(_data.loc[:, "actual_payout"])
    return premium_balance


def at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    post_mortem: bool = False,
    use_pure_premium: bool = True,
    **kwargs,
) -> float:
    """Compute the premium balance at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the balance.
        post_mortem: If True, only include policies with expiration date <= date.
            Defaults to False.
        use_pure_premium: If True, use pure premium instead of total premium.
            Defaults to True.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The difference between total premiums and actual payouts at the given date.
    """
    if use_pure_premium is True:
        premium_column = "pure_premium"
    else:
        premium_column = "premium"

    mask_premium = data.start <= date
    mask_payout = data.expired_on <= date

    if post_mortem is True:
        mask_premium &= data.expiration <= date
        mask_payout &= (data.expiration <= date) & data.actual_payout.notna() & data.expired_on.notna()

    premium_balance = (
        data.loc[mask_premium, premium_column].sum() - data.loc[mask_payout].actual_payout.sum()
    )
    return premium_balance


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    use_pure_premium: bool = True,
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of premium balances.

    Policies are divided into batches based on their expected expiration date
    (period_column = "expiration") or actual expiration date (period_column = "expired_on").
    For each batch, the function computes the difference between premiums and payouts.
    If cumulative is True, the values represent cumulative balances over time.

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute cumulative balances over time.
            Defaults to False.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        use_pure_premium: If True, use pure premium instead of total premium.
            Defaults to True.
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "expiration" or
            "expired_on". Defaults to "expiration".
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing premium balances indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    if use_pure_premium is True:
        premium_column = "pure_premium"
    else:
        premium_column = "premium"

    assert premium_column in data.columns, f"{premium_column} column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "expiration column is required"

    _data = data.copy()

    # Transform dates in regular intervals
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)
    _data = _data.groupby("date").agg({premium_column: "sum", "actual_payout": lambda x: np.nansum(x)})

    if cumulative:
        _data[premium_column] = _data[premium_column].cumsum()
        _data["actual_payout"] = _data.actual_payout.cumsum()

    _data["premium_balance"] = _data[premium_column] - _data["actual_payout"]

    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["premium_balance"]
