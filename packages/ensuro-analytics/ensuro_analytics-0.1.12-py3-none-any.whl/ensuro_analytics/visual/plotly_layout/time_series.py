"""Plotly layout utilities for time series visualizations.

This module provides functionality to create time series plots using Plotly,
including:
- Single metric plotting with volume
- Multi-channel metric plotting
- Custom color schemes
- Percentage formatting
- Interactive hover information
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


def _colorway() -> list[str]:
    """Get the list of colors from the Plotly colorway.

    Returns:
        A list of color strings from the current Plotly colorway.
    """
    return pio.templates[pio.templates.default].layout.colorway


def plot(
    fig: go.Figure,
    metric: pd.Series,
    cumulative: bool,
    label: str,
    volume: pd.Series | None = None,
    benchmark: float = None,
    percent_axis: bool | None = True,
) -> go.Figure:
    """Create a time series plot using Plotly.

    This function creates an interactive visualization of a metric over time,
    with options for:
    - Volume overlay on secondary axis
    - Benchmark line
    - Percentage formatting
    - Custom styling and markers
    - Interactive hover information

    Args:
        fig: Plotly figure to plot on.
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
        The updated Plotly figure containing the visualization.
    """
    if cumulative:
        title = f"Cumulative {label}".title()
    else:
        title = f"Rolling {label}".title()

    fig.add_trace(
        go.Scatter(
            x=metric.index,
            y=metric.values,
            name=title,
            mode="lines+markers",
            marker={
                "color": "white",
                "size": 10,
                "line": {"color": _colorway()[0], "width": 3},
            },
            line={"color": _colorway()[0]},
        ),
        secondary_y=False,
    )

    if volume is not None:
        fig.add_trace(
            go.Scatter(
                x=volume.index,
                y=volume.values,
                name="Volume",
                mode="lines+markers",
                marker={
                    "color": "white",
                    "size": 10,
                    "line": {"color": _colorway()[1], "width": 2},
                    "symbol": "diamond",
                },
                line={"color": _colorway()[1]},
                opacity=0.7,
            ),
            secondary_y=True,
        )

    if benchmark is not None:
        fig.add_trace(
            go.Scatter(
                x=metric.index,
                y=np.ones(len(metric.index)) * benchmark,
                hoverinfo="skip",
                mode="lines",
                line={"color": "red", "dash": "dash"},
                name="Benchmark",
            ),
            secondary_y=False,
        )

    if percent_axis:
        fig.update_yaxes(tickformat="p", secondary_y=False)

    if volume is not None:
        fig.update_yaxes(title="Volume", secondary_y=True, showgrid=False, side="right")

    fig.update_yaxes(
        secondary_y=False,
        title=title,
        showgrid=False,
        side="left",
        title_font=dict(color=_colorway()[0]),
    )
    fig.update_xaxes(title="Date")
    fig.update_layout(showlegend=False)

    if volume is not None:
        fig.update_yaxes(title_font=dict(color=_colorway()[1]), secondary_y=True)

    fig.update_layout(hovermode="x", hoverlabel=dict(font=dict(color="white"), bgcolor=_colorway()[0]))

    return fig


def plot_by_primary_channel(
    fig: go.Figure,
    metric_dic: dict[str, pd.Series],
    cumulative: bool,
    label: str,
    benchmark: float = None,
    percent_axis: bool | None = True,
) -> go.Figure:
    """Create a time series plot comparing metrics across channels using Plotly.

    This function creates an interactive visualization comparing a metric across
    different channels, with options for:
    - Multiple channels with different colors
    - Benchmark line
    - Percentage formatting
    - Custom styling and markers
    - Interactive hover information

    Args:
        fig: Plotly figure to plot on.
        metric_dic: Dictionary mapping channel names to their metric Series.
        cumulative: Whether the data represents cumulative or rolling values.
        label: Label for the y-axis.
        benchmark: Optional benchmark value to plot as a horizontal line.
            Defaults to None.
        percent_axis: Whether to format the y-axis as percentage.
            Defaults to True.

    Returns:
        The updated Plotly figure containing the visualization.
    """
    if cumulative:
        title = f"Cumulative {label}".title()
    else:
        title = f"Rolling {label}".title()

    for i, (channel, metric) in enumerate(metric_dic.items()):
        fig.add_trace(
            go.Scatter(
                x=metric.index,
                y=metric.values,
                name=channel,
                mode="lines+markers",
                marker={
                    "color": "white",
                    "size": 10,
                    "line": {"color": _colorway()[i], "width": 3},
                },
                line={"color": _colorway()[i]},
            ),
            secondary_y=False,
        )

    all_indices = pd.concat([metric for (_, metric) in metric_dic.items()]).index
    idx = pd.Index([all_indices.min(), all_indices.max()])

    if benchmark is not None:
        fig.add_trace(
            go.Scatter(
                x=idx,
                y=np.ones(len(idx)) * benchmark,
                hoverinfo="skip",
                mode="lines",
                line={"color": "red", "dash": "dash"},
                name="Benchmark",
            ),
            secondary_y=False,
        )

    if percent_axis:
        fig.update_yaxes(tickformat="p", secondary_y=False)

    fig.update_yaxes(title=title, secondary_y=False, showgrid=False, side="left")
    fig.update_xaxes(title="Date")
    fig.update_layout(showlegend=True)

    return fig
