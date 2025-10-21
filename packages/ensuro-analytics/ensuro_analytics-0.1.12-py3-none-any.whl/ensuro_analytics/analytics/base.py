"""Base functionality for analytics operations."""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class Constants:
    """Container for constant values used throughout the analytics module.

    Attributes:
        day: A pandas Timedelta representing one day.
    """

    day: pd.Timedelta = pd.Timedelta("1D")


def today() -> pd.Timestamp:
    """Get today's date normalized to midnight.

    Returns:
        A pandas Timestamp representing today at midnight.
    """
    return pd.to_datetime("today").normalize()


def _timestamp(date: Any) -> pd.Timestamp:
    """Convert any date-like input to a normalized pandas Timestamp.

    Args:
        date: Any date-like input that can be converted to a pandas Timestamp.

    Returns:
        A normalized pandas Timestamp.
    """
    return pd.Timestamp(date).normalize()


def active_at_t(data: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
    """Check which policies were active at a given date.

    Args:
        data: DataFrame containing policy data.
        date: The date to check for active policies.

    Returns:
        A boolean Series indicating which policies were active at the given date.
    """
    mask = data.expired_on.isna() | (data.expired_on > _timestamp(date))
    mask &= data.start <= _timestamp(date)
    return mask


def _between(
    dates: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    include_left: bool = True,
    include_right: bool = True,
) -> pd.Series:
    """Find dates that fall between a start and end date.

    Args:
        dates: DataFrame containing dates to check.
        start_date: The start of the date range.
        end_date: The end of the date range.
        include_left: Whether to include the start date in the range.
            Defaults to True.
        include_right: Whether to include the end date in the range.
            Defaults to True.

    Returns:
        A boolean Series indicating which dates fall within the specified range.
    """
    mask = np.ones(len(dates)).astype(bool)

    if include_left is True:
        mask &= dates >= start_date
    else:
        mask &= dates > start_date

    if include_right is True:
        mask &= dates <= end_date
    else:
        mask &= dates < end_date

    return mask


def expired_between(
    data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    include_left: bool = True,
    include_right: bool = True,
) -> pd.Series:
    """Find policies that expired between two dates.

    Args:
        data: DataFrame containing policy data.
        start_date: The start of the date range.
        end_date: The end of the date range.
        include_left: Whether to include the start date in the range.
            Defaults to True.
        include_right: Whether to include the end date in the range.
            Defaults to True.

    Returns:
        A boolean Series indicating which policies expired within the specified range.
    """
    return _between(
        data.expired_on,
        start_date=start_date,
        end_date=end_date,
        include_left=include_left,
        include_right=include_right,
    )


def started_between(
    data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    include_left: bool = True,
    include_right: bool = True,
) -> pd.Series:
    """Find policies that started between two dates.

    Args:
        data: DataFrame containing policy data.
        start_date: The start of the date range.
        end_date: The end of the date range.
        include_left: Whether to include the start date in the range.
            Defaults to True.
        include_right: Whether to include the end date in the range.
            Defaults to True.

    Returns:
        A boolean Series indicating which policies started within the specified range.
    """
    return _between(
        data.start,
        start_date=start_date,
        end_date=end_date,
        include_left=include_left,
        include_right=include_right,
    )


def _count_payouts(series: pd.Series) -> int:
    """Count the number of non-zero payouts in a series.

    Args:
        series: Series containing payout values.

    Returns:
        The count of non-zero payouts.
    """
    return ((~np.isnan(series)) & (series > 1e-9)).sum()


def find_first_date(
    data: pd.DataFrame,
    splitters: list[str],
    date_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Find the date of the first policy sold for each group.

    Args:
        data: DataFrame containing policy data.
        splitters: List of columns to group by.
        date_column: Name of the column containing dates. Defaults to "start".
        **kwargs: Additional keyword arguments passed to groupby.

    Returns:
        A Series containing the first date for each group, indexed to match the input data.
    """
    sorted_data = data.copy().sort_values(by=date_column)
    first_dates = sorted_data.groupby(splitters)[date_column].transform("min").dt.date

    return first_dates.reindex(data.index).copy()


constants = Constants()
