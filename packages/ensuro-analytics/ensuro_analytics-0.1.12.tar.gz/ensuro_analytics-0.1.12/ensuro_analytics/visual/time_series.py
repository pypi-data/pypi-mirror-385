"""Utilities for generating time series visualizations.

This module provides functionality to create time series plots for various metrics,
including:
- Single metric plotting with volume
- Multi-channel metric plotting
- Support for both Plotly and Matplotlib backends
- Configurable time periods and frequencies
"""

from importlib import import_module

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ensuro_analytics.analytics.base import _timestamp, constants, today
from ensuro_analytics.analytics.portfolio.total_policies import time_series as total_policies_time_series
from ensuro_analytics.visual.matplotlib_layout import time_series as matplotlib_layout
from ensuro_analytics.visual.plotly_layout import time_series as plotly_layout

AVAILABLE_METRICS = [
    "active_policies",
    "active_premium",
    "collected_premium",
    "default_percentage",
    "junior_scr",
    "loss_ratio",
    "loss_to_exposure",
    "n_payouts",
    "payouts",
    "premium_balance",
    "scr",
    "senior_scr",
    "total_policies",
    "var",
]

METRICS_PATH = "..analytics.portfolio.{}"


def plot(
    data: pd.DataFrame,
    metric: str,
    fig: go.Figure | plt.Figure,
    cumulative: bool | None = True,
    freq: str | None = "1W",
    period_column: str | None = "expiration",
    post_mortem: bool | None = True,
    with_volume: bool | None = True,
    benchmark: float | None = None,
    percent: bool | None = False,
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    **kwargs,
) -> go.Figure | plt.Figure:
    """Generate a time series plot for a specific metric.

    This function creates a visualization of a metric over time, with options for:
    - Cumulative or rolling calculations
    - Volume overlay
    - Benchmark line
    - Percentage formatting
    - Custom date ranges

    Args:
        data: DataFrame containing the metric data.
        metric: Name of the metric to plot (must be in AVAILABLE_METRICS).
        fig: Figure object (Plotly or Matplotlib).
        cumulative: Whether to plot cumulative or rolling values. Defaults to True.
        freq: Temporal frequency for aggregation. Defaults to "1W" (weekly).
        period_column: Name of the column to use as time. Defaults to "expiration".
        post_mortem: Whether to plot only policies with expiration <= max expired_on.
            Defaults to True.
        with_volume: Whether to plot volume as a secondary axis. Defaults to True.
        benchmark: Benchmark value to plot as a horizontal line. Defaults to None.
        percent: Whether to format y-axis as percentage. Defaults to False.
        end_date: End date for the plot. If None, uses today's date.
        start_date: Start date for the plot. If None, uses 90 days before today.
        **kwargs: Additional arguments passed to the metric's time_series function.

    Returns:
        A Plotly or Matplotlib figure containing the visualization.

    Raises:
        AssertionError: If the specified metric is not in AVAILABLE_METRICS.
    """
    assert (
        metric in AVAILABLE_METRICS
    ), f"Metric {metric} not available. Available metrics: {AVAILABLE_METRICS}"

    data = data.copy()

    module = import_module(METRICS_PATH.format(metric), package="ensuro_analytics.visual")

    ts = module.time_series(
        data,
        cumulative=cumulative,
        freq=freq,
        end_date=end_date,
        start_date=start_date,
        period_column=period_column,
        port_mortem=post_mortem,
        percent=True,
        **kwargs,
    )

    if with_volume:
        volume = total_policies_time_series(
            data,
            cumulative=cumulative,
            freq=freq,
            end_date=end_date,
            start_date=start_date,
            port_mortem=post_mortem,
            period_column=period_column,
        )
    else:
        volume = None

    if isinstance(fig, go.Figure):
        return plotly_layout.plot(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            volume=volume,
            benchmark=benchmark,
            percent_axis=percent,
        )
    elif isinstance(fig, plt.Figure):
        return matplotlib_layout.plot(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            volume=volume,
            benchmark=benchmark,
            percent_axis=percent,
        )


def plot_by_primary_channel(
    data: pd.DataFrame,
    metric: str,
    fig: go.Figure | plt.Figure,
    primary_channel: str = "partner",
    cumulative: bool = True,
    freq: str = "1W",
    period_column: str = "expiration",
    post_mortem: bool = True,
    benchmark: float = None,
    n_channel: int = 5,
    percent: bool = False,
    end_date: pd.Timestamp | str = today(),
    start_date: pd.Timestamp | str = today() - 90 * constants.day,
) -> go.Figure | plt.Figure:
    """Generate a time series plot showing metrics by primary channel.

    This function creates a visualization comparing a metric across different channels,
    with options for:
    - Top N channels by volume
    - Cumulative or rolling calculations
    - Benchmark line
    - Percentage formatting
    - Custom date ranges

    Args:
        data: DataFrame containing the metric data.
        metric: Name of the metric to plot (must be in AVAILABLE_METRICS).
        fig: Figure object (Plotly or Matplotlib).
        primary_channel: Name of the column to use for channel grouping.
            Defaults to "partner".
        cumulative: Whether to plot cumulative or rolling values. Defaults to True.
        freq: Temporal frequency for aggregation. Defaults to "1W" (weekly).
        period_column: Name of the column to use as time. Defaults to "expiration".
        post_mortem: Whether to plot only policies with expiration <= max expired_on.
            Defaults to True.
        benchmark: Benchmark value to plot as a horizontal line. Defaults to None.
        n_channel: Number of top channels to plot. Defaults to 5.
        percent: Whether to format y-axis as percentage. Defaults to False.
        end_date: End date for the plot. Can be Timestamp or string. If None, uses today.
        start_date: Start date for the plot. Can be Timestamp or string. If None, uses
            90 days before today.

    Returns:
        A Plotly or Matplotlib figure containing the visualization.

    Raises:
        AssertionError: If the specified metric is not in AVAILABLE_METRICS.
    """
    assert (
        metric in AVAILABLE_METRICS
    ), f"Metric {metric} not available. Available metrics: {AVAILABLE_METRICS}"

    # Turn start_date and end_date to datetime
    if isinstance(start_date, str):
        start_date = _timestamp(start_date)
    if isinstance(end_date, str):
        end_date = _timestamp(end_date)

    _data = data.copy()

    module = import_module(METRICS_PATH.format(metric), package="ensuro_analytics.visual")

    mask = np.ones(_data.shape[0], dtype=bool)
    if start_date is not None:
        mask &= _data[period_column] >= start_date
    if end_date is not None:
        mask &= _data[period_column] <= end_date

    channels = _data[mask][primary_channel].value_counts().head(n_channel).index
    ts = {}

    for ch in channels:
        ts[ch] = module.time_series(
            _data[_data[primary_channel] == ch],
            cumulative=cumulative,
            freq=freq,
            end_date=end_date,
            start_date=start_date,
            period_column=period_column,
            percent=percent,
            post_mortem=post_mortem,
        )

    if isinstance(fig, go.Figure):
        return plotly_layout.plot_by_primary_channel(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            benchmark=benchmark,
            percent_axis=percent,
        )
    elif isinstance(fig, plt.Figure):
        return matplotlib_layout.plot_by_primary_channel(
            fig,
            ts,
            cumulative,
            label=metric.replace("_", " "),
            benchmark=benchmark,
            percent_axis=percent,
        )
