"""Utilities for setting up visualization data for eToken metrics.

This module provides functionality to prepare and transform data for visualization,
including:
- Data normalization and standardization
- Time series aggregation
- Performance metrics calculation
- Market data integration
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.etokens.base import TimeUnits


def prepare_data(
    data: pd.DataFrame,
    full_ur: bool = False,
    time_resolution: str | TimeUnits = "1D",
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
) -> pd.DataFrame:
    """Prepare data for visualization.

    This function processes and transforms data for visualization by:
    - Computing daily returns
    - Aggregating data to specified frequency
    - Normalizing dates and timezones
    - Handling missing values

    Args:
        data: DataFrame containing eToken metrics with a multi-index of eToken and date.
        full_ur: Whether to use perfect returns (full unrealized returns) instead of
            nominal returns. Defaults to False.
        time_resolution: Time resolution for the return calculation. Can be a string
            (e.g., "1D") or TimeUnits object. Defaults to "1D" (daily).
        freq: Frequency for the time series. Defaults to "1W" (weekly).
        end_date: Maximum date for the time series. If None, uses today's date.
        start_date: Minimum date for the time series. If None, uses 90 days before today.

    Returns:
        A DataFrame containing processed data ready for visualization.

    Note:
        The start date is adjusted to ensure sufficient data for the first calculation,
        considering both the frequency and time resolution parameters.
    """
    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    # Localize the dates as UTC if they are not localized
    if start_date.tz is None:
        start_date = start_date.tz_localize("UTC")

    if end_date.tz is None:
        end_date = end_date.tz_localize("UTC")

    freq_unit = TimeUnits("1" + freq[-1])
    freq_days = int(freq[:-1]) * freq_unit.n_days_in_unit

    start_date = max(
        start_date,
        data.index.get_level_values("date").min() + pd.Timedelta(f"{freq_days}D"),
        data.index.get_level_values("date").min() + pd.Timedelta(f"{time_resolution.n_days_in_unit}D"),
    )

    ts_dates = pd.date_range(start=start_date, end=end_date, freq=freq, tz="UTC")

    # Compute daily returns
    daily_returns_df = pd.DataFrame(index=data.index, columns=["returns"])
    daily_returns_df["returns"] = data.groupby(level="e_token").total_supply.pct_change()

    # Compute perfect returns (full unrealized returns)
    daily_returns_df["perfect_returns"] = daily_returns_df["returns"].copy()
    daily_returns_df.loc[daily_returns_df["perfect_returns"].isnull(), "perfect_returns"] = 0

    # Add dividend returns
    daily_returns_df["returns"] += data["dividend"] / data["total_supply"]
    daily_returns_df["perfect_returns"] += data["dividend"] / data["total_supply"]

    # Add insurance returns
    daily_returns_df["returns"] += data["dividend_insurance"]
    daily_returns_df["perfect_returns"] += data["dividend_insurance"]

    # Compute time series
    ts = pd.Series(
        index=ts_dates,
        data=[
            daily_returns_df.loc[daily_returns_df.index.get_level_values("date") < date, "returns"].mean()
            for date in ts_dates
        ],
    )

    # Create visualization DataFrame
    viz_data = pd.DataFrame(index=ts_dates)
    viz_data["returns"] = ts
    viz_data["cumulative_returns"] = (1 + ts).cumprod()
    viz_data["volatility"] = ts.rolling(window=20).std() * np.sqrt(252)
    viz_data["sharpe_ratio"] = ts.rolling(window=20).mean() / ts.rolling(window=20).std() * np.sqrt(252)
    viz_data["sortino_ratio"] = (
        ts.rolling(window=20).mean() / ts[ts < 0].rolling(window=20).std() * np.sqrt(252)
    )
    viz_data["max_drawdown"] = (
        viz_data["cumulative_returns"].rolling(window=20).max() / viz_data["cumulative_returns"] - 1
    )

    return viz_data


def add_market_data(
    viz_data: pd.DataFrame,
    market_data: pd.DataFrame,
    market_col: str = "returns",
) -> pd.DataFrame:
    """Add market data to visualization DataFrame.

    This function integrates market data into the visualization DataFrame by:
    - Aligning dates and timezones
    - Computing market metrics
    - Adding correlation calculations

    Args:
        viz_data: DataFrame containing processed eToken data.
        market_data: DataFrame containing market data with a date index.
        market_col: Column name for market returns in market_data. Defaults to "returns".

    Returns:
        A DataFrame containing both eToken and market data ready for visualization.
    """
    # Ensure market data has UTC timezone
    if market_data.index.tz is None:
        market_data.index = market_data.index.tz_localize("UTC")

    # Add market data
    viz_data["market_returns"] = market_data[market_col]
    viz_data["market_cumulative_returns"] = (1 + market_data[market_col]).cumprod()
    viz_data["market_volatility"] = market_data[market_col].rolling(window=20).std() * np.sqrt(252)
    viz_data["market_sharpe_ratio"] = (
        market_data[market_col].rolling(window=20).mean()
        / market_data[market_col].rolling(window=20).std()
        * np.sqrt(252)
    )
    viz_data["market_sortino_ratio"] = (
        market_data[market_col].rolling(window=20).mean()
        / market_data[market_col][market_data[market_col] < 0].rolling(window=20).std()
        * np.sqrt(252)
    )
    viz_data["market_max_drawdown"] = (
        viz_data["market_cumulative_returns"].rolling(window=20).max()
        / viz_data["market_cumulative_returns"]
        - 1
    )

    # Add correlation
    viz_data["correlation"] = viz_data["returns"].rolling(window=20).corr(viz_data["market_returns"])

    return viz_data
