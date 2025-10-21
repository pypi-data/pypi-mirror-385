"""Functions for computing loss-to-exposure ratios.

This module provides functionality to calculate the ratio of actual payouts to potential
payouts (exposure) for insurance policies at specific points in time and over time series,
with options for post-mortem analysis and cumulative calculations.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.portfolio.base import date_to_period

REQUIRED_COLUMNS = ["actual_payout", "payout", "start", "expired_on", "expiration"]


def current_value(data: pd.DataFrame, post_mortem: bool = False, **kwargs) -> float:
    """Compute the current loss-to-exposure ratio.

    Args:
        data: DataFrame containing policy data.
        post_mortem: If True, only include policies with expiration date <= today.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The ratio of actual payouts to potential payouts, expressed as a percentage.
    """
    _data = data.copy()
    if post_mortem:
        pm_mask = (_data.expiration <= today()) & (_data.expired_on.notna()) & (_data.actual_payout.notna())
        _data = _data.loc[pm_mask]

    loss_to_exposure = _data.actual_payout.sum() / _data.payout.sum()
    loss_to_exposure *= 100

    return loss_to_exposure


def at_t(data: pd.DataFrame, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """Compute the loss-to-exposure ratio at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the ratio.
        post_mortem: If True, only include policies with expiration date <= date.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The ratio of actual payouts to potential payouts at the given date,
        expressed as a percentage. Returns 0 if there are no applicable policies.
    """
    if post_mortem is True:
        mask = (data.expiration <= date) & data.actual_payout.notna() & data.expired_on.notna()
    else:
        mask = np.ones(len(data), dtype=bool)

    mask &= data.start <= date
    # Compute loss-to-exposure ratio
    if not any(mask):
        return 0
    x = data.loc[mask, "actual_payout"].sum() / data.loc[mask, "payout"].sum()

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
    """Compute a time series of loss-to-exposure ratios.

    Policies are divided into batches based on their expected expiration date
    (period_column = "expiration") or actual expiration date (period_column = "expired_on").
    For each batch, the function computes the ratio of actual payouts to potential
    payouts. If cumulative is True, the ratios are computed using cumulative values.

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute ratios using cumulative values over time.
            Defaults to False.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "start",
            "expired_on", or "expiration". Defaults to "expiration".
        percent: If True, express ratios as decimals rather than percentages.
            Defaults to False.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing loss-to-exposure ratios indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    assert "payout" in data.columns, "payout column is required"
    assert "actual_payout" in data.columns, "actual_payout column is required"
    assert period_column in data.columns, "period column is required"

    data = data[~data[period_column].isna()].copy()

    data["date"] = date_to_period(dates=data[period_column], freq=freq)
    data = data.groupby("date").agg({"payout": "sum", "actual_payout": "sum"})

    if cumulative is True:
        data["payout"] = data.payout.cumsum()
        data["actual_payout"] = data.actual_payout.cumsum()

    data["loss_to_exposure"] = data.actual_payout / data.payout

    if (percent is False) or (percent is None):
        data["loss_to_exposure"] *= 100

    if start_date is not None:
        data = data.loc[data.index >= start_date]
    if end_date is not None:
        data = data.loc[data.index <= end_date]
    return data["loss_to_exposure"]


def rolling_at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    timedelta: pd.Timedelta = pd.Timedelta(days=7),
    **kwargs,
) -> float:
    """Compute the loss-to-exposure ratio for policies within a time window.

    Args:
        data: DataFrame containing policy data.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The ratio of actual payouts to potential payouts for policies with
        expiration dates within the specified time window, expressed as a
        percentage. Returns 0 if there are no applicable policies.
    """
    mask = (data.expiration > date - timedelta) & (data.expiration <= date + timedelta)
    mask = mask & data.actual_payout.notna() & data.expired_on.notna()
    if not any(mask):
        return 0
    x = data.loc[mask, "actual_payout"].sum() / data.loc[mask, "payout"].sum()

    return 100 * x
