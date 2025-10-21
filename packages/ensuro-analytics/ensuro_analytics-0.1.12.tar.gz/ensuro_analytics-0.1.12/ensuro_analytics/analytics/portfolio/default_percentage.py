"""Functions for computing default percentages of insurance policies.

This module provides functionality to calculate the percentage of policies that have
defaulted (resulted in payouts) at specific points in time and over time series.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import _count_payouts, constants, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "start", "expired_on", "expiration"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """Compute the current default percentage of policies.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, only consider policies with expiration <= today.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The percentage of policies that have defaulted (as a percentage).
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]

    # Count policies with actual_payout > 1e-9 (numerator) and total policies (denominator)
    numerator = (_data.actual_payout.fillna(0) > 1e-9).sum()
    denominator = len(_data)
    default_percentage = numerator / denominator if denominator > 0 else np.nan
    default_percentage *= 100

    return default_percentage


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """Compute the default percentage at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the default percentage.
        post_mortem: If True, only consider policies with expiration <= date.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The percentage of policies that had defaulted at the given date
        (as a percentage).
    """
    if post_mortem is True:
        mask = (data.expiration <= date) & data.actual_payout.notna() & data.expired_on.notna()
    else:
        mask = np.ones(len(data), dtype=bool)

    mask &= data.start <= date

    # Compute default percentage
    if not any(mask):
        return 0
    x = _count_payouts(data.loc[mask].actual_payout.values) / data.loc[mask].shape[0]

    return 100 * x


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "expiration",
    percent: bool = False,
    **kwargs,
) -> pd.Series:
    """Compute a time series of default percentages.

    Policies are divided into batches based on their expected expiration date
    (period_column = "expiration") or actual expiration date (period_column = "expired_on").
    For each batch, the function computes the percentage of policies that defaulted.

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute cumulative default percentages (i.e., using all
            policies up to each date). Defaults to False.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "expired_on" or
            "expiration". Defaults to "expiration".
        percent: If True, express default percentages as decimals rather than
            percentages. Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing default percentages indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "period column is required"

    data = data[~data[period_column].isna()].copy()

    data["claimed"] = data.actual_payout > 1e-9

    # Transform dates into regular intervals
    data["date"] = date_to_period(dates=data[period_column], freq=freq)

    data = data.groupby("date").agg({"claimed": "sum", "actual_payout": "count"})

    if cumulative:
        data["claimed"] = data.claimed.cumsum()
        data["actual_payout"] = data.actual_payout.cumsum()

    data["default_percentage"] = data.claimed / data.actual_payout
    if not percent:
        data["default_percentage"] *= 100

    if start_date is not None:
        data = data.loc[data.index >= start_date]
    if end_date is not None:
        data = data.loc[data.index <= end_date]
    return data["default_percentage"]


def rolling_at_t(
    data: pd.DataFrame, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
) -> float:
    """Compute the default percentage for policies expiring within a time window.

    Args:
        data: DataFrame containing policy data.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The percentage of policies that defaulted within the time window
        (as a percentage).
    """
    mask = (data.expiration > date - timedelta) & (data.expiration <= date + timedelta)
    mask = mask & data.actual_payout.notna() & data.expired_on.notna()
    if not any(mask):
        return 0
    x = _count_payouts(data.loc[mask].actual_payout.values) / data.loc[mask].shape[0]

    return 100 * x
