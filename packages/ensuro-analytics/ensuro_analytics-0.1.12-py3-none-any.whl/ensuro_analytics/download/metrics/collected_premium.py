"""BigQuery functions for computing collected insurance premiums.

This module provides functionality to calculate the total value of premiums collected
from expired insurance policies at specific points in time and over time series using BigQuery.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

REQUIRED_COLUMNS = ["premium", "start", "expired_on"]


def current_value(bq: "BigQueryInterface", **kwargs) -> float:
    """Compute the current value of collected premiums.

    Args:
        bq: BigQueryInterface instance for executing queries.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums from all expired (inactive) policies.
    """
    # Build base WHERE clause
    where_conditions = ["expired_on IS NOT NULL", "expired_on <= CURRENT_TIMESTAMP()"]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as collected_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["collected_premium"])


def at_t(bq: "BigQueryInterface", date: pd.Timestamp, **kwargs) -> float:
    """Compute the value of collected premiums at a specific point in time.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to compute collected premiums.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums from policies that expired before the given date.
    """
    # Build base WHERE clause
    where_conditions = ["expired_on IS NOT NULL", f"expired_on < '{bq._format_timestamp(date)}'"]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as collected_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["collected_premium"])


def time_series(
    bq: "BigQueryInterface",
    freq: str = "1W",
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of collected premium values.

    Args:
        bq: BigQueryInterface instance for executing queries.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing collected premium values indexed by date.
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = pd.Timestamp.now()
    if start_date is None:
        start_date = end_date - pd.Timedelta(days=90)

    date_series_cte = bq._generate_date_series_cte(start_date, end_date, freq)

    # Build join conditions
    join_conditions = ["p.expired_on IS NOT NULL", "p.expired_on < DATETIME(d.period_date)"]

    # If filters exist, add them to the join
    filter_clause = bq.generate_filter_clause("")
    if filter_clause:
        filter_clause = filter_clause.replace("WHERE ", "")
        from_clause = f"""
        FROM date_series d
        LEFT JOIN {bq.get_table_name()} p
            ON {' AND '.join(join_conditions)}
            AND {filter_clause}
        """
    else:
        from_clause = f"""
        FROM date_series d
        LEFT JOIN {bq.get_table_name()} p
            ON {' AND '.join(join_conditions)}
        """

    query = f"""
    WITH {date_series_cte}
    SELECT
        d.period_date,
        COALESCE(SUM(p.premium), 0) as collected_premiums
    {from_clause}
    GROUP BY d.period_date
    ORDER BY d.period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["collected_premiums"].values,
        index=pd.to_datetime(result["period_date"]),
        name="collected_premiums",
    )


def rolling_at_t(
    bq: "BigQueryInterface",
    date: pd.Timestamp,
    timedelta: pd.Timedelta = pd.Timedelta(days=7),
    **kwargs,
) -> float:
    """Compute the value of collected premiums within a time window.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of pure premiums from policies that expired within the time window.
    """
    start_date = date - timedelta
    end_date = date + timedelta

    # Build WHERE clause - matching pandas logic: (start_date, end_date]
    where_conditions = [
        "expired_on IS NOT NULL",
        f"expired_on > '{bq._format_timestamp(start_date)}'",
        f"expired_on <= '{bq._format_timestamp(end_date)}'",
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as rolling_collected_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """

    result = bq.execute_query(query)
    return float(result.iloc[0]["rolling_collected_premium"])
