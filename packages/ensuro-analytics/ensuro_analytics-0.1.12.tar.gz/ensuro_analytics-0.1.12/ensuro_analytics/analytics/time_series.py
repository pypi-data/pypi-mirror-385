"""
Utils to create time-series data from a table of policies.
"""

import pandas as pd

from ensuro_analytics.analytics.portfolio.active_policies import at_t as active_policies_at_t
from ensuro_analytics.analytics.portfolio.active_premium import at_t as active_premium_at_t
from ensuro_analytics.analytics.portfolio.collected_premium import at_t as won_premium_at_t
from ensuro_analytics.analytics.portfolio.collected_premium import rolling_at_t as won_premium_rolling_at_t
from ensuro_analytics.analytics.portfolio.default_percentage import at_t as default_percentage_at_t
from ensuro_analytics.analytics.portfolio.default_percentage import (
    rolling_at_t as default_percentage_rolling_at_t,
)
from ensuro_analytics.analytics.portfolio.loss_ratio import at_t as loss_ratio_at_t
from ensuro_analytics.analytics.portfolio.loss_ratio import rolling_at_t as loss_ratio_rolling_at_t
from ensuro_analytics.analytics.portfolio.n_payouts import at_t as n_payouts_at_t
from ensuro_analytics.analytics.portfolio.payouts import at_t as payout_at_t
from ensuro_analytics.analytics.portfolio.post_mortem_premium import at_t as post_mortem_premium_at_t
from ensuro_analytics.analytics.portfolio.scr import at_t as scr_at_t
from ensuro_analytics.analytics.portfolio.total_policies import at_t as total_policies_at_t
from ensuro_analytics.analytics.portfolio.total_policies import rolling_at_t as total_policies_rolling_at_t


def compute_aggregate_metrics(data: pd.DataFrame, date: pd.Timestamp) -> tuple:
    """Compute several different analytics metrics at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: Timestamp at which to compute the metrics.

    Returns:
        A tuple containing the following metrics in order:
        - active_premium: Premium for active policies
        - inactive_premium: Premium for inactive policies
        - active_policies: Number of active policies
        - total_policies: Total number of policies
        - total_payouts: Total amount of payouts
        - num_payouts: Number of payouts
        - total_scr_used: Total SCR used
        - loss_ratio: Current loss ratio
        - rolling_loss_ratio: Rolling window loss ratio
        - default_percentage: Current default percentage
        - rolling_default_percentage: Rolling window default percentage
        - rolling_n_policies: Rolling window number of policies
        - rolling_premium: Rolling window premium
        - post_mortem_premium: Post-mortem premium
    """
    active_premium = active_premium_at_t(data, date)
    inactive_premium = won_premium_at_t(data, date)
    active_policies = active_policies_at_t(data, date)
    total_policies = total_policies_at_t(data, date)
    total_payouts = payout_at_t(data, date)
    num_payouts = n_payouts_at_t(data, date)
    total_scr_used = scr_at_t(data, date)
    loss_ratio = loss_ratio_at_t(data, date)
    rolling_loss_ratio = loss_ratio_rolling_at_t(data, date)
    default_percentage = default_percentage_at_t(data, date)
    rolling_default_percentage = default_percentage_rolling_at_t(data, date)
    rolling_n_policies = total_policies_rolling_at_t(data, date)
    rolling_premium = won_premium_rolling_at_t(data, date)
    post_mortem_premium = post_mortem_premium_at_t(data, date)

    results = (
        active_premium,
        inactive_premium,
        active_policies,
        total_policies,
        total_payouts,
        num_payouts,
        total_scr_used,
        loss_ratio,
        rolling_loss_ratio,
        default_percentage,
        rolling_default_percentage,
        rolling_n_policies,
        rolling_premium,
        post_mortem_premium,
    )

    return results


def build_time_series_dataframe(data: pd.DataFrame, freq: str = "1W") -> pd.DataFrame:
    """Aggregate the policy dataset into a time series of metrics.

    The metrics are computed for each date and product combination.

    Args:
        data: DataFrame containing policy data.
        freq: Frequency for time series aggregation. Defaults to "1W" (weekly).

    Returns:
        DataFrame containing time series metrics with the following columns:
        - date: Timestamp
        - rm_name: Risk module name
        - active_premium: Premium for active policies
        - inactive_premium: Premium for inactive policies
        - active_policies: Number of active policies
        - total_policies: Total number of policies
        - total_payouts: Total amount of payouts
        - num_payouts: Number of payouts
        - total_scr_used: Total SCR used
        - loss_ratio: Current loss ratio
        - rolling_loss_ratio: Rolling window loss ratio
        - default_perc: Current default percentage
        - rolling_default_perc: Rolling window default percentage
        - rolling_n_policies: Rolling window number of policies
        - rolling_premium: Rolling window premium
        - post_mortem_premium: Post-mortem premium
    """
    start_date = data.start.min().normalize()
    end_date = pd.to_datetime("today").normalize()

    dates = pd.date_range(start=start_date, end=end_date, normalize=True, freq=freq)
    time_series = pd.DataFrame(dates, columns=["date"])

    def get_data():
        return data.copy()

    # Fill values
    new_columns = [
        "rm_name",
        "active_premium",
        "inactive_premium",
        "active_policies",
        "total_policies",
        "total_payouts",
        "num_payouts",
        "total_scr_used",
        "loss_ratio",
        "rolling_loss_ratio",
        "default_perc",
        "rolling_default_perc",
        "rolling_n_policies",
        "rolling_premium",
        "post_mortem_premium",
    ]

    time_series[new_columns] = pd.DataFrame.from_records(
        time_series["date"].apply((lambda x: compute_aggregate_metrics(get_data(), x)))
    ).values

    return time_series
