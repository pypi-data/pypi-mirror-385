"""
This module contains functions to compute post mortem premium.
"""

import pandas as pd

from ensuro_analytics.analytics.base import constants, today

REQUIRED_COLUMNS = ["expiration", "premium"]


def current_value(data: pd.DataFrame, **kwargs) -> float:
    """
    Computes the current overall post-mortem premium.
    """
    return at_t(
        data,
        today(),
    )


def at_t(data: pd.DataFrame, date: pd.Timedelta, **kwargs) -> float:
    """
    Computes the post mortem premium at time t.
    """
    mask = data.expiration <= date
    return data.loc[mask].premium.sum()


def time_series(
    data: pd.DataFrame,
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of post-mortem premium values.

    Policies are divided into batches based on their expected expiration date.
    For each batch, the function computes the post-mortem premium (premium from
    expired policies only).

    Args:
        data: DataFrame containing policy data.
        cumulative: If True, compute cumulative post-mortem premium values over time.
            Defaults to False.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. If None, use the maximum date in the
            period column. Defaults to today.
        start_date: Minimum date to include. If None, use the minimum date in the
            period column. Defaults to 90 days before today.
        period_column: Column to use for period grouping. Can be "expiration".
            Defaults to "expiration".
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing post-mortem premium values indexed by date.

    Raises:
        AssertionError: If required columns are missing from the data.
    """
    from ensuro_analytics.analytics.portfolio.base import date_to_period

    assert "premium" in data.columns, "premium column is required"
    assert "expiration" in data.columns, "expiration column is required"
    assert period_column in data.columns, "period column is required"

    # Filter out rows with NaN in the period column
    _data = data[~data[period_column].isna()].copy()

    # Transform dates into regular intervals
    _data["date"] = date_to_period(dates=_data[period_column], freq=freq)

    # Group by date and sum premiums
    _data = _data.groupby("date").agg({"premium": "sum"})

    if cumulative:
        _data["premium"] = _data.premium.cumsum()

    # Filter by start and end date
    if start_date is not None:
        _data = _data.loc[_data.index >= start_date]
    if end_date is not None:
        _data = _data.loc[_data.index <= end_date]

    return _data["premium"]
