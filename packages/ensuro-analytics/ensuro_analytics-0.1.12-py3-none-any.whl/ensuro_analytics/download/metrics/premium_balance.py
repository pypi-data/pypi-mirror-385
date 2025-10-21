"""BigQuery functions for computing insurance premium balances.

This module provides functionality to calculate the balance between premiums collected
and payouts made for insurance policies at specific points in time and over time series,
with options for post-mortem analysis and using pure premiums using BigQuery.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

REQUIRED_COLUMNS = ["premium", "pure_premium", "actual_payout", "expiration", "expired_on", "start"]


def current_value(
    bq: "BigQueryInterface",
    post_mortem: bool = False,
    use_pure_premium: bool = True,
    **kwargs,
) -> float:
    """Compute the current premium balance.

    Args:
        bq: BigQueryInterface instance for executing queries.
        post_mortem: If True, only include policies with expiration date <= today.
        use_pure_premium: If True, use pure premium instead of total premium.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The difference between total premiums and actual payouts.
    """
    premium_column = "pure_premium" if use_pure_premium else "premium"

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
    SELECT 
        COALESCE(SUM({premium_column}), 0) - COALESCE(SUM(actual_payout), 0) as premium_balance
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["premium_balance"])


def at_t(
    bq: "BigQueryInterface",
    date: pd.Timestamp,
    post_mortem: bool = False,
    use_pure_premium: bool = True,
    **kwargs,
) -> float:
    """Compute the premium balance at a specific point in time.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to compute the balance.
        post_mortem: If True, only include policies with expiration date <= date.
        use_pure_premium: If True, use pure premium instead of total premium.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The difference between total premiums and actual payouts at the given date.
    """
    premium_column = "pure_premium" if use_pure_premium else "premium"

    # Build WHERE clauses for each CTE
    premium_conditions = [f"start <= '{bq._format_timestamp(date)}'"]
    payout_conditions = [f"expired_on <= '{bq._format_timestamp(date)}'"]

    if post_mortem:
        premium_conditions.append(f"expiration <= '{bq._format_timestamp(date)}'")
        payout_conditions.extend(
            [
                f"expiration <= '{bq._format_timestamp(date)}'",
                "expired_on IS NOT NULL",
                "actual_payout IS NOT NULL",
            ]
        )

    premium_where = "WHERE " + " AND ".join(premium_conditions)
    payout_where = "WHERE " + " AND ".join(payout_conditions)

    # Apply filters
    premium_where = bq.generate_filter_clause(premium_where)
    payout_where = bq.generate_filter_clause(payout_where)

    query = f"""
    WITH premium_sum AS (
        SELECT COALESCE(SUM({premium_column}), 0) as total_premium
        FROM {bq.get_table_name()}
        {premium_where}
    ),
    payout_sum AS (
        SELECT COALESCE(SUM(actual_payout), 0) as total_payout
        FROM {bq.get_table_name()}
        {payout_where}
    )
    SELECT total_premium - total_payout as premium_balance
    FROM premium_sum, payout_sum
    """

    result = bq.execute_query(query)
    return float(result.iloc[0]["premium_balance"])


def time_series(
    bq: "BigQueryInterface",
    cumulative: bool = False,
    freq: str = "1W",
    use_pure_premium: bool = True,
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str = "expiration",
    **kwargs,
) -> pd.Series:
    """Compute a time series of premium balances.

    Args:
        bq: BigQueryInterface instance for executing queries.
        cumulative: If True, compute cumulative balances over time.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        use_pure_premium: If True, use pure premium instead of total premium.
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing premium balances indexed by date.
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = pd.Timestamp.now()
    if start_date is None:
        start_date = end_date - pd.Timedelta(days=90)

    premium_column = "pure_premium" if use_pure_premium else "premium"
    date_trunc = bq._freq_to_date_trunc(freq)

    # Build WHERE clause
    where_conditions = [
        f"{period_column} BETWEEN '{bq._format_timestamp(start_date)}' AND '{bq._format_timestamp(end_date)}'"
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    WITH period_data AS (
        SELECT
            DATE_TRUNC(DATE({period_column}), {date_trunc}) as period_date,
            SUM({premium_column}) as premium_sum,
            SUM(actual_payout) as payout_sum
        FROM {bq.get_table_name()}
        {where_clause}
        GROUP BY period_date
    )
    SELECT
        period_date,
        {'SUM(premium_sum) OVER (ORDER BY period_date) - SUM(payout_sum) OVER (ORDER BY period_date)'
    if cumulative else 'premium_sum - payout_sum'} as premium_balance
    FROM period_data
    ORDER BY period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["premium_balance"].values, index=pd.to_datetime(result["period_date"]), name="premium_balance"
    )
