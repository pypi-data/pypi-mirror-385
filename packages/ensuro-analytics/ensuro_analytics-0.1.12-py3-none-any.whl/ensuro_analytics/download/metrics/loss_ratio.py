"""BigQuery functions to compute loss ratios for insurance policies.

This module provides functions to calculate various loss ratio metrics for a portfolio
of insurance policies using BigQuery queries, including current values, time series,
and rolling windows.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

REQUIRED_COLUMNS = ["pure_premium", "actual_payout", "expiration", "expired_on"]


def current_value(bq: "BigQueryInterface", post_mortem: bool = False, **kwargs) -> float:
    """Compute the current loss ratio for a set of policies.

    Args:
        bq: BigQueryInterface instance for executing queries.
        post_mortem: If True, compute loss ratio only for expired policies.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The loss ratio as a percentage.
    """
    # Build base WHERE clause
    where_conditions = []
    if post_mortem:
        where_conditions.extend(
            ["expiration <= CURRENT_TIMESTAMP()", "expired_on IS NOT NULL", "actual_payout IS NOT NULL"]
        )

    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    else:
        where_clause = ""

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT 
        SUM(actual_payout) / NULLIF(SUM(pure_premium), 0) * 100 as loss_ratio
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["loss_ratio"])


def at_t(bq: "BigQueryInterface", date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
    """Compute the loss ratio at a specific point in time.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to compute the loss ratio.
        post_mortem: If True, compute loss ratio only for expired policies.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The loss ratio as a percentage.
    """
    # Build base WHERE clause - always include start filter
    where_conditions = [f"start <= '{bq._format_timestamp(date)}'"]
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
    SELECT 
        SUM(actual_payout) / NULLIF(SUM(pure_premium), 0) * 100 as loss_ratio
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["loss_ratio"])


def time_series(
    bq: "BigQueryInterface",
    cumulative: bool = False,
    freq: str = "1W",
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str | None = "expiration",
    percent: bool | None = False,
    **kwargs,
) -> pd.Series:
    """Compute a time series of loss ratios.

    Args:
        bq: BigQueryBase instance for executing queries.
        cumulative: If True, compute cumulative loss ratios.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        percent: If True, express as decimals rather than percentages.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing loss ratios indexed by date.
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = pd.Timestamp.now()
    if start_date is None:
        start_date = end_date - pd.Timedelta(days=90)

    date_trunc = bq._freq_to_date_trunc(freq)
    multiplier = 1 if percent else 100

    # Build WHERE clause
    where_conditions = [
        f"{period_column} IS NOT NULL",
        f"{period_column} BETWEEN '{bq._format_timestamp(start_date)}' AND '{bq._format_timestamp(end_date)}'",
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    WITH period_metrics AS (
        SELECT
            DATE_TRUNC(DATE({period_column}), {date_trunc}) as period_date,
            SUM(pure_premium) as total_premium,
            SUM(actual_payout) as total_payout
        FROM {bq.get_table_name()}
        {where_clause}
        GROUP BY period_date
    )
    SELECT
        period_date,
        {'SUM(total_payout) OVER (ORDER BY period_date) / NULLIF(SUM(total_premium) OVER (ORDER BY period_date), 0)'
    if cumulative else 'total_payout / NULLIF(total_premium, 0)'} * {multiplier} as loss_ratio
    FROM period_metrics
    ORDER BY period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["loss_ratio"].values, index=pd.to_datetime(result["period_date"]), name="loss_ratio"
    )


def rolling_at_t(
    bq: "BigQueryInterface",
    date: pd.Timestamp,
    timedelta: pd.Timedelta = pd.Timedelta(days=7),
    **kwargs,
) -> float:
    """Compute the loss ratio for policies expiring within a time window.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: Center of the time window.
        timedelta: Half-width of the time window. Defaults to 7 days.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The loss ratio as a percentage.
    """
    start_date = date - timedelta
    end_date = date + timedelta

    # Build WHERE clause
    where_conditions = [
        f"expiration > '{bq._format_timestamp(start_date)}'",
        f"expiration <= '{bq._format_timestamp(end_date)}'",
        "actual_payout IS NOT NULL",
        "expired_on IS NOT NULL",
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT 
        SUM(actual_payout) / NULLIF(SUM(pure_premium), 0) * 100 as rolling_loss_ratio
    FROM {bq.get_table_name()}
    {where_clause}
    """

    result = bq.execute_query(query)
    return float(result.iloc[0]["rolling_loss_ratio"])
