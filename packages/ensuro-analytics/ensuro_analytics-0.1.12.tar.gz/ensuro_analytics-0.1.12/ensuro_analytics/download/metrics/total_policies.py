"""BigQuery functions for computing total insurance policy counts.

This module provides functionality to calculate the total number of policies sold
at specific points in time and over time series, with options for post-mortem analysis
and cumulative counting using BigQuery.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

REQUIRED_COLUMNS = ["expiration", "start", "pure_premium", "premium"]


def current_value(bq: "BigQueryInterface", post_mortem: bool = False, **kwargs) -> int:
    """Compute the current total number of policies sold.

    Args:
        bq: BigQueryInterface instance for executing queries.
        post_mortem: If True, only count policies with expiration date <= today.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The total number of policies sold that meet the criteria.
    """
    # Build base WHERE clause
    where_conditions = []
    if post_mortem:
        where_conditions.append("expiration <= CURRENT_TIMESTAMP()")

    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COUNT(*) as total_policies
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return int(result.iloc[0]["total_policies"])


def at_t(bq: "BigQueryInterface", date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> int:
    """Compute the total number of policies sold at a specific point in time.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to count policies.
        post_mortem: If True, only count policies with expiration date <= date.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The total number of policies sold that meet the criteria at the given date.
    """
    # Build base WHERE clause
    where_conditions = [f"start <= '{bq._format_timestamp(date)}'"]
    if post_mortem:
        where_conditions.append(f"expiration <= '{bq._format_timestamp(date)}'")

    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COUNT(*) as total_policies
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return int(result.iloc[0]["total_policies"])


def time_series(
    bq: "BigQueryInterface",
    freq: str = "1W",
    cumulative: bool = False,
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of total policy counts.

    Args:
        bq: BigQueryInterface instance for executing queries.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        cumulative: If True, compute cumulative policy counts over time.
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing policy counts indexed by date.
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = pd.Timestamp.now()
    if start_date is None:
        start_date = end_date - pd.Timedelta(days=90)

    date_trunc = bq._freq_to_date_trunc(freq)

    # Build WHERE clause
    where_conditions = [
        f"{period_column} BETWEEN '{bq._format_timestamp(start_date)}' AND '{bq._format_timestamp(end_date)}'"
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    WITH policy_counts AS (
        SELECT
            DATE_TRUNC(DATE({period_column}), {date_trunc}) as period_date,
            COUNT(*) as policy_count
        FROM {bq.get_table_name()}
        {where_clause}
        GROUP BY period_date
    )
    SELECT
        period_date,
        {'SUM(policy_count) OVER (ORDER BY period_date)' if cumulative else 'policy_count'} as total_policies
    FROM policy_counts
    ORDER BY period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["total_policies"].values, index=pd.to_datetime(result["period_date"]), name="total_policies"
    )


def rolling_at_t(
    bq: "BigQueryInterface",
    date: pd.Timestamp,
    timedelta: pd.Timedelta = pd.Timedelta(days=7),
    **kwargs,
) -> int:
    """Compute the number of policies sold within a time window.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The number of policies sold within the specified time window.
    """
    start_date = date - timedelta
    end_date = date + timedelta

    # Build WHERE clause
    where_conditions = [
        f"start BETWEEN '{bq._format_timestamp(start_date)}' AND '{bq._format_timestamp(end_date)}'"
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COUNT(*) as rolling_policies
    FROM {bq.get_table_name()}
    {where_clause}
    """

    result = bq.execute_query(query)
    return int(result.iloc[0]["rolling_policies"])
