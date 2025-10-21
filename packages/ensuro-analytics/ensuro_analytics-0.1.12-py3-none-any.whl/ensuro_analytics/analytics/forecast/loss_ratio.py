import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import today
from ensuro_analytics.analytics.forecast.base import ForecastResult
from ensuro_analytics.analytics.portfolio.loss_to_exposure import (
    current_value as loss_to_exposure_current_value,
)

REQUIRED_COLUMNS = ["pure_premium", "actual_payout", "expiration", "expired_on"]


def forecast(
    data: pd.DataFrame,
    split_on: str | list[str] | None = None,
    past_horizon: int = 90,
    only_on_active: bool = True,
    n_simulations: int = 1000,
    forecasted_loss_to_exposure: np.ndarray | pd.Series | None = None,
) -> ForecastResult:
    """
    Forecast the loss ratio for the portfolio.
    """

    if forecasted_loss_to_exposure is not None:
        assert len(forecasted_loss_to_exposure) == len(
            data
        ), "The forecasted loss-to-exposure ratio must have the same length as the data"
        if isinstance(forecasted_loss_to_exposure, np.ndarray):
            forecasted_loss_to_exposure = pd.Series(forecasted_loss_to_exposure)
        loss_to_exposure_column = forecasted_loss_to_exposure
    else:
        loss_to_exposure_column = _forecast_loss_to_exposure_standard(data, past_horizon, split_on)

    if only_on_active is True:
        mask = ~data.actual_payout.isna()
    else:
        mask = np.ones(len(data), dtype=bool)

    loss_to_exposure_column = loss_to_exposure_column[mask].values
    payouts = data.payout[mask].values

    # Sample random numbers
    simulations = np.random.random(size=(len(loss_to_exposure_column), n_simulations))
    # Generate outcomes
    outcomes = (simulations < loss_to_exposure_column[:, np.newaxis]).astype(int)
    # Compute payouts
    outcomes = outcomes * payouts[:, np.newaxis]

    # Compute total payouts
    total_payouts = outcomes.sum(axis=0)

    # Compute total loss_ratios
    total_loss_ratios = total_payouts / data.loc[mask].pure_premium.sum()

    return ForecastResult(total_loss_ratios)


def _forecast_loss_to_exposure_standard(
    data: pd.DataFrame, past_horizon: int = 90, split_on: str | list[str] | None = None
):
    """
    Forecast the loss-to-exposure ratio for the portfolio. The forecast is very simple: it assumes that the
    loss-to-exposure for each policy will be equal to the average loss-to-exposure observed in the last
    past_horizon days for the same group of policies. Policies are grouped by the columns in split_on.
    """
    if split_on is None:
        split_on = ["rm_name"]

    # First, compute the observed loss-to-exposure for the different groups
    if isinstance(split_on, str):
        split_on = [split_on]
    # Create the mask to select recent policies
    mask = data.start >= today() - pd.Timedelta(days=past_horizon)
    # Make post-mortem
    mask &= data.expiration <= today()
    loss_to_exposures = (
        data.loc[mask].groupby(split_on).apply(lambda x: loss_to_exposure_current_value(x) / 100.0).to_dict()
    )
    # Then, simulate forward
    # Create a tuple from the split_on columns to match the keys in loss_to_exposures
    if len(split_on) == 1:
        group_keys = data[split_on[0]]
    else:
        group_keys = data[split_on].apply(tuple, axis=1)
    # Map the loss_to_exposure values back to the DataFrame
    loss_to_exposure_column = group_keys.map(loss_to_exposures)
    return loss_to_exposure_column
