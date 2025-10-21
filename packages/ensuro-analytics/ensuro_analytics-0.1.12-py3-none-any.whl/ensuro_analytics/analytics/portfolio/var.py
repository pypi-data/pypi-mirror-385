"""Functions for computing Value at Risk (VaR) metrics for insurance portfolios.

This module provides functions to calculate various VaR metrics through Monte Carlo
simulation, including current values, point-in-time values, and time series.
"""

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import active_at_t, constants, today

REQUIRED_COLUMNS = ["payout", "loss_prob", "expiration", "start", "expired_on"]


def current_value(
    data: pd.DataFrame,
    level: float | int | list[float] | list[int] | None = 90.0,
    n_simulations: int = 1000,
    payout_pct: float = 1.0,
    random_state: int | np.random.Generator | None = None,
    **kwargs,
) -> float | list[float]:
    """
    Compute the current Value at Risk (VaR) for the portfolio.

    VaR is a measure of the potential loss in value of a portfolio, given a specific
    confidence level and time horizon. This function uses Monte Carlo simulation to
    estimate the VaR for the current active policies in the portfolio.

    Args:
        data: DataFrame containing policy data.
        level: The confidence level(s) for the VaR calculation. Can be a single value
            or a list of values. Defaults to 90.0.
        n_simulations: The number of simulations to run for the Monte Carlo estimation.
            Defaults to 1000.
        payout_pct: The payout percentage to apply to the losses. Defaults to 1.0.
        random_state: Seed or generator for random number generation.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The VaR value(s) for the portfolio.
    """

    # Active policies
    mask = active_at_t(data, today())
    active_data = data.loc[mask]

    # Random values for simulation
    rng = np.random.default_rng(random_state)
    random_values = rng.random((n_simulations, len(active_data)))
    simulated_triggered = random_values < active_data["loss_prob"].values

    # Simulated losses, including the payout ratio
    simulated_losses = simulated_triggered * active_data["payout"].values * payout_pct

    # Compute total payouts
    total_payouts = simulated_losses.sum(axis=1)

    # Compute VaR
    var = np.percentile(total_payouts, level)

    return var


def at_t(
    data: pd.DataFrame,
    date: pd.Timestamp,
    level: float | int | list[float] | list[int] | None = 90.0,
    n_simulations: int = 1000,
    payout_pct: float = 1.0,
    random_state: int | np.random.Generator | None = None,
    **kwargs,
) -> float | list[float]:
    """
    Compute the Value at Risk (VaR) for the portfolio at a specific point in time.

    Args:
        data: DataFrame containing policy data.
        date: The timestamp at which to compute the VaR.
        level: The confidence level(s) for the VaR calculation. Can be a single value
            or a list of values. Defaults to 90.0.
        n_simulations: The number of simulations to run for the Monte Carlo estimation.
            Defaults to 1000.
        payout_pct: The payout percentage to apply to the losses. Defaults to 1.0.
        random_state: Seed or generator for random number generation.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The VaR value(s) for the portfolio at the given date.
    """

    # Active policies
    mask = active_at_t(data, date)
    active_data = data.loc[mask]

    # Random values for simulation
    rng = np.random.default_rng(random_state)
    random_values = rng.random((n_simulations, len(active_data)))
    simulated_triggered = random_values < active_data["loss_prob"].values

    # Simulated losses, including the payout ratio
    simulated_losses = simulated_triggered * active_data["payout"].values * payout_pct

    # Compute total payouts
    total_payouts = simulated_losses.sum(axis=1)

    # Compute VaR
    var = np.percentile(total_payouts, level)

    return var


def time_series(
    data: pd.DataFrame,
    level: float | int | list[float] | list[int] | None = 90.0,
    n_simulations: int = 1000,
    payout_pct: float = 1.0,
    freq: str = "1W",
    end_date: pd.Timestamp | None = today(),
    start_date: pd.Timestamp | None = today() - 90 * constants.day,
    random_state: int | np.random.Generator | None = None,
    **kwargs,
) -> pd.Series | pd.DataFrame:
    """
    Compute a time series of Value at Risk (VaR) values for the portfolio.

    Args:
        data: DataFrame containing policy data.
        level: The confidence level(s) for the VaR calculation. Can be a single value
            or a list of values. Defaults to 90.0.
        n_simulations: The number of simulations to run for the Monte Carlo estimation.
            Defaults to 1000.
        payout_pct: The payout percentage to apply to the losses. Defaults to 1.0.
        freq: Frequency of the time series. Defaults to "1W" (weekly).
        end_date: Maximum date to include. Defaults to today.
        start_date: Minimum date to include. Defaults to 90 days before today.
        random_state: Seed or generator for random number generation.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        A series or a dataframe of VaR time series.
    """

    # Generate dates
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)

    # Initialize the output series
    if isinstance(level, (int, float)):
        var_series = pd.Series(index=dates)
    else:
        var_series = pd.DataFrame(index=dates, columns=level)

    # Create a random number generator to draw seeds per date
    base_rng = np.random.default_rng(random_state)
    seeds = base_rng.integers(low=0, high=2**32 - 1, size=len(dates))

    # Compute VaR for each date
    for i, date in enumerate(dates):
        var_series.loc[date] = at_t(
            data,
            date,
            level=level,
            n_simulations=n_simulations,
            payout_pct=payout_pct,
            random_state=seeds[i],
        )

    return var_series
