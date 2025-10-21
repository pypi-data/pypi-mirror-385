"""Functions to compute loss ratios for insurance policies.

This module provides functions to calculate various loss ratio metrics for a portfolio
of insurance policies, including current values, time series, and rolling windows.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = ["start", "pure_premium", "actual_payout", "expiration", "expired_on"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """Compute the current loss ratio for a set of policies.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, compute loss ratio only for policies with expiration
            date <= today. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The loss ratio as a percentage.
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]
    loss_ratio = _data.actual_payout.sum() / _data.pure_premium.sum() * 100
    return loss_ratio


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """Compute the loss ratio at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the loss ratio.
        post_mortem: If True, compute loss ratio only for policies with expiration
            date <= date. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The loss ratio as a percentage.
    """
    if post_mortem is True:
        mask = (data.expiration <= date) & data.actual_payout.notna() & data.expired_on.notna()
    else:
        mask = np.ones(len(data), dtype=bool)

    mask &= data.start <= date

    if not any(mask.values):
        return 0
    # Compute loss ratio
    x = data.loc[mask].actual_payout.sum() / data.loc[mask].pure_premium.sum()

    return 100 * x


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str | None = "expiration",
    percent: bool | None = False,
    **kwargs,
) -> pd.Series:
    """Compute a time series of loss ratios.

    Policies are divided into batches based on their expected expiration date
    (period_column = "expiration") or actual expiration date (period_column = "expired_on").
    For each batch, the function computes the policies' loss ratio.

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute cumulative loss ratios (i.e., using all policies
            up to each date). Defaults to False.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the period
            column. Defaults to today().
        start_date: Minimum date to include. If None, use the minimum date in the period
            column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "expiration" or
            "expired_on". Defaults to "expiration".
        percent: If True, express loss ratios as decimals rather than percentages.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing loss ratios indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "pure_premium" in data.columns, "pure_premium column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "period column is required"

    data = data[~data[period_column].isna()].copy()

    data["date"] = date_to_period(dates=data[period_column], freq=freq)
    data = data.groupby("date").agg({"pure_premium": "sum", "actual_payout": "sum"})

    if cumulative:
        data["pure_premium"] = data.pure_premium.cumsum()
        data["actual_payout"] = data.actual_payout.cumsum()

    data["loss_ratio"] = data.actual_payout / data.pure_premium
    if not percent:
        data["loss_ratio"] *= 100

    if start_date is not None:
        data = data.loc[data.index >= start_date]
    if end_date is not None:
        data = data.loc[data.index <= end_date]
    return data["loss_ratio"]


def rolling_at_t(
    data: pd.DataFrame, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7)
) -> float:
    """Compute the loss ratio for policies expiring within a time window.

    Args:
        data: DataFrame containing policy data.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.

    Returns:
        The loss ratio as a percentage.
    """
    mask = (data.expiration > date - timedelta) & (data.expiration <= date + timedelta)
    mask = mask & data.actual_payout.notna() & data.expired_on.notna()
    x = data.loc[mask].actual_payout.sum() / data.loc[mask].pure_premium.sum()

    return 100 * x
