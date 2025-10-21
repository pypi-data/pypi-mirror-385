"""BigQuery functions for computing and analyzing premiums of active insurance policies.

This module provides functionality to calculate premium values for active policies
at specific points in time and over time series using BigQuery.
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ensuro_analytics.download.bigquery import BigQueryInterface

REQUIRED_COLUMNS = ["premium", "expired_on", "start"]


def current_value(bq: "BigQueryInterface", **kwargs) -> float:
    """Compute the current total value of active premium.

    Args:
        bq: BigQueryInterface instance for executing queries.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums for all currently active policies.
    """
    # Build base WHERE clause
    where_conditions = [
        "start <= CURRENT_TIMESTAMP()",
        "(expired_on IS NULL OR expired_on > CURRENT_TIMESTAMP())",
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as active_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["active_premium"])


def at_t(bq: "BigQueryInterface", date: pd.Timestamp, **kwargs) -> float:
    """Compute the total premium value of active policies at a specific point in time.

    Args:
        bq: BigQueryInterface instance for executing queries.
        date: The timestamp at which to compute active premiums.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The sum of premiums for all policies active at the given date.
    """
    # Build base WHERE clause
    where_conditions = [
        f"start <= '{bq._format_timestamp(date)}'",
        f"(expired_on IS NULL OR expired_on > '{bq._format_timestamp(date)}')",
    ]
    where_clause = "WHERE " + " AND ".join(where_conditions)

    # Apply filters
    where_clause = bq.generate_filter_clause(where_clause)

    query = f"""
    SELECT COALESCE(SUM(premium), 0) as active_premium
    FROM {bq.get_table_name()}
    {where_clause}
    """
    result = bq.execute_query(query)
    return float(result.iloc[0]["active_premium"])


def time_series(
    bq: "BigQueryInterface",
    freq: str = "1W",
    end_date: pd.Timestamp | None = None,
    start_date: pd.Timestamp | None = None,
    period_column: str = "start",
    **kwargs,
) -> pd.Series:
    """Compute a time series of active premium values.

    Args:
        bq: BigQueryInterface instance for executing queries.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        period_column: Column to use for period grouping.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A Series containing active premium values indexed by date.
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = pd.Timestamp.now()
    if start_date is None:
        start_date = end_date - pd.Timedelta(days=90)

    date_series_cte = bq._generate_date_series_cte(start_date, end_date, freq)

    # Build WHERE clause for the join condition
    join_conditions = [
        "p.start <= DATETIME(d.period_date)",
        "(p.expired_on IS NULL OR p.expired_on > DATETIME(d.period_date))",
    ]

    # If filters exist, we need to add them to the FROM clause
    filter_clause = bq.generate_filter_clause("")
    if filter_clause:
        # Remove the "WHERE " prefix
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
        COALESCE(SUM(p.premium), 0) as active_premiums
    {from_clause}
    GROUP BY d.period_date
    ORDER BY d.period_date
    """

    result = bq.execute_query(query)
    return pd.Series(
        result["active_premiums"].values, index=pd.to_datetime(result["period_date"]), name="active_premiums"
    )
