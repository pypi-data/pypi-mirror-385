"""Matplotlib layout utilities for time series visualizations.

This module provides functionality to create time series plots using Matplotlib,
including:
- Single metric plotting with volume
- Multi-channel metric plotting
- Custom color schemes
- Percentage formatting
"""

import warnings

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


def _colorway() -> list[str]:
    """Get the list of colors from the Matplotlib color cycle.

    Returns:
        A list of color strings from the current Matplotlib color cycle.
    """
    return matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]


def percentage_formatter(percentage: float, pos: int) -> str:
    """Format a number as a percentage string.

    Args:
        percentage: The number to format.
        pos: The position of the tick (unused).

    Returns:
        A string representing the number as a percentage with one decimal place.
    """
    return f"{percentage * 100:.1f}%"


def plot(
    fig: plt.Figure,
    metric: pd.Series,
    cumulative: bool,
    label: str,
    volume: pd.Series | None = None,
    benchmark: float | None = None,
    percent_axis: bool | None = True,
) -> plt.Figure:
    """Create a time series plot using Matplotlib.

    This function creates a visualization of a metric over time, with options for:
    - Volume overlay on secondary axis
    - Benchmark line
    - Percentage formatting
    - Custom styling and markers

    Args:
        fig: Matplotlib figure to plot on.
        metric: Series containing the metric data to plot.
        cumulative: Whether the data represents cumulative or rolling values.
        label: Label for the y-axis.
        volume: Optional Series containing volume data for secondary axis.
            Defaults to None.
        benchmark: Optional benchmark value to plot as a horizontal line.
            Defaults to None.
        percent_axis: Whether to format the y-axis as percentage.
            Defaults to True.

    Returns:
        The updated Matplotlib figure containing the visualization.
    """
    if cumulative:
        title = f"Cumulative {label}".title()
    else:
        title = f"Rolling {label}".title()

    ax1 = fig.gca()

    ax1.plot(
        metric.index,
        metric.values,
        color=_colorway()[0],
        markerfacecolor="w",
        marker="o",
        markersize=12,
        lw=2,
        markeredgewidth=4,
        label=title,
    )
    ax1.set_ylabel(title, color=_colorway()[0])

    if volume is not None:
        ax2 = ax1.twinx()
        ax2.plot(
            volume.index,
            volume.values,
            markerfacecolor="w",
            markersize=12,
            lw=2,
            markeredgewidth=4,
            color=_colorway()[1],
            marker="D",
            label="Volume",
            alpha=0.7,
        )
        ax2.set_ylabel("Volume", color=_colorway()[1])
        ax2.spines["right"].set_visible(True)

    if benchmark is not None:
        ax1.axhline(
            benchmark,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Benchmark",
        )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if percent_axis:
            ax1.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # set the dates in the x-axis in the format MM-DD
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d-%m"))
    ax1.set_xlabel("Date")
    fig.tight_layout()

    plt.close()

    return fig


def plot_by_primary_channel(
    fig: plt.Figure,
    metric_dic: dict[str, pd.Series],
    cumulative: bool,
    label: str,
    benchmark: float | None = None,
    percent_axis: bool | None = True,
) -> plt.Figure:
    """Create a time series plot comparing metrics across channels using Matplotlib.

    This function creates a visualization comparing a metric across different channels,
    with options for:
    - Multiple channels with different colors
    - Benchmark line
    - Percentage formatting
    - Custom styling and markers

    Args:
        fig: Matplotlib figure to plot on.
        metric_dic: Dictionary mapping channel names to their metric Series.
        cumulative: Whether the data represents cumulative or rolling values.
        label: Label for the y-axis.
        benchmark: Optional benchmark value to plot as a horizontal line.
            Defaults to None.
        percent_axis: Whether to format the y-axis as percentage.
            Defaults to True.

    Returns:
        The updated Matplotlib figure containing the visualization.
    """
    if cumulative:
        title = f"Cumulative {label}".title()
    else:
        title = f"Rolling {label}".title()

    ax1 = fig.gca()

    for i, (channel, metric) in enumerate(metric_dic.items()):
        ax1.plot(
            metric.index,
            metric.values,
            color=_colorway()[i],
            markerfacecolor="w",
            marker="o",
            markersize=12,
            lw=2,
            markeredgewidth=4,
            label=channel,
        )

    if benchmark is not None:
        ax1.axhline(
            benchmark,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Benchmark",
        )

    ax1.set_ylabel(title)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if percent_axis:
            ax1.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # set the dates in the x-axis in the format MM-DD
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d-%m"))
    ax1.set_xlabel("Date")

    ax1.legend(frameon=False, loc=(1.05, 0.5))

    fig.tight_layout()

    plt.close()

    return fig
