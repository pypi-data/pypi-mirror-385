"""BigQuery functions to compute post mortem premium.

This module contains functions to compute post mortem premium
from policies that have already expired - using BigQuery.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

import pandas as pd

REQUIRED_COLUMNS = ["expiration", "premium"]


def current_value(bq: "BigQueryInterface", **kwargs) -> float:
    """Computes the current overall post-mortem premium.

    Args:
        bq: BigQueryInterface instance for executing queries.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums from policies that have expired.
    """
    # Build base WHERE clause
    where_conditions = ["expiration <= CURRENT_TIMESTAMP()"]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as post_mortem_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["post_mortem_premium"])


def at_t(bq: "BigQueryInterface", date: pd.Timestamp, **kwargs) -> float:
    """Computes the post mortem premium at time t.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to compute the post mortem premium.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums from policies that expired before the given date.
    """
    # Build base WHERE clause
    where_conditions = [f"expiration <= '{bq._format_timestamp(date)}'"]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as post_mortem_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["post_mortem_premium"])


def time_series(
    bq: "BigQueryInterface",
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of post-mortem premium values.

    Args:
        bq: BigQueryInterface instance for executing queries.
        cumulative: If True, compute cumulative post-mortem premium values over time.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing post-mortem premium values indexed by date.
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = pd.Timestamp.now()
    if start_date is None:
        start_date = end_date - pd.Timedelta(days=90)

    date_trunc = bq._freq_to_date_trunc(freq)

    # Build WHERE clause
    where_conditions = [
        f"{period_column} IS NOT NULL",
        f"{period_column} BETWEEN '{bq._format_timestamp(start_date)}' AND '{bq._format_timestamp(end_date)}'",
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    WITH period_data AS (
        SELECT
            DATE_TRUNC(DATE({period_column}), {date_trunc}) as period_date,
            SUM(premium) as premium_sum
        FROM {bq.get_table_name()}
        {where_clause}
        GROUP BY period_date
    )
    SELECT
        period_date,
        {'SUM(premium_sum) OVER (ORDER BY period_date)' if cumulative else 'premium_sum'} as premium
    FROM period_data
    ORDER BY period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["premium"].values,
        index=pd.to_datetime(result["period_date"]),
        name="premium",
    )
