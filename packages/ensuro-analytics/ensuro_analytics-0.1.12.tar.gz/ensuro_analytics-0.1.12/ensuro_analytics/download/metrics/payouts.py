"""BigQuery functions for computing insurance policy payouts.

This module provides functionality to calculate the total value of payouts made for
insurance policies at specific points in time and over time series, with options for
post-mortem analysis and cumulative calculations using BigQuery.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

REQUIRED_COLUMNS = ["actual_payout", "expiration", "expired_on"]


def current_value(bq: "BigQueryInterface", post_mortem: bool = False, **kwargs) -> float:
    """Compute the current total value of payouts.

    Args:
        bq: BigQueryInterface instance for executing queries.
        post_mortem: If True, only include payouts for policies with expiration <= today.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of all payouts that meet the criteria.
    """
    # Build base WHERE clause
    where_conditions = []
    if post_mortem:
        where_conditions.extend(
            ["expiration <= CURRENT_TIMESTAMP()", "expired_on IS NOT NULL", "actual_payout IS NOT NULL"]
        )

    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(actual_payout), 0) as total_payouts
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["total_payouts"])


def at_t(bq: "BigQueryInterface", date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """Compute the total value of payouts at a specific point in time.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to compute payouts.
        post_mortem: If True, only include payouts for policies with expiration <= date.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of all payouts that meet the criteria at the given date.
    """
    # Build base WHERE clause
    where_conditions = [f"expired_on <= '{bq._format_timestamp(date)}'"]
    if post_mortem:
        where_conditions.extend(
            [
                f"expiration <= '{bq._format_timestamp(date)}'",
                "expired_on IS NOT NULL",
                "actual_payout IS NOT NULL",
            ]
        )

    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(actual_payout), 0) as total_payouts
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["total_payouts"])


def time_series(
    bq: "BigQueryInterface",
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of payout values.

    Args:
        bq: BigQueryInterface instance for executing queries.
        cumulative: If True, compute cumulative payout values over time.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing payout values indexed by date.
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
    WITH payout_data AS (
        SELECT
            DATE_TRUNC(DATE({period_column}), {date_trunc}) as period_date,
            SUM(actual_payout) as payout_sum
        FROM {bq.get_table_name()}
        {where_clause}
        GROUP BY period_date
    )
    SELECT
        period_date,
        {'SUM(payout_sum) OVER (ORDER BY period_date)' if cumulative else 'payout_sum'} as actual_payout
    FROM payout_data
    ORDER BY period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["actual_payout"].values, index=pd.to_datetime(result["period_date"]), name="actual_payout"
    )
