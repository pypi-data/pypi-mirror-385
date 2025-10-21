"""
Portfolio review functionality for analyzing insurance policy portfolios.
"""

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ensuro_analytics.analytics.base import constants, today
from ensuro_analytics.analytics.dataframe import create_ensuro_accessors


def _get_var(
    data: pd.DataFrame, level: float | int | list[float] | list[int], **kwargs
) -> float | list[float]:
    """Get Value at Risk (VaR) for given levels.

    Args:
        data: DataFrame containing the data to compute VaR on.
        level: Single level or list of levels for VaR computation.
        **kwargs: Additional arguments passed to the VaR computation.

    Returns:
        Single VaR value or list of VaR values for each level.
    """
    if isinstance(level, float | int):
        level = [level]
    try:
        return data.var.current_value(level=level, **kwargs)
    except ValueError:
        return [np.nan] * len(level)


def compute_adjusted_target_loss_ratio(
    data: pd.DataFrame,
    target_loss_ratio: float,
    tau_1: float = 30 * 3,
    tau_2: float = 30 * 3,
    lower_bound: float = 0.0,
    upper_bound: float = 1.0,
    pct_trend: float = 1.0,
    consider_active_policies: bool = True,
) -> tuple[float, float]:
    """Compute the adjusted target loss ratio based on historical performance.

    This function adjusts the target loss ratio based on historical surplus and expected
    future exposure. It takes into account both expired and active policies.

    Args:
        data: DataFrame containing the portfolio data.
        target_loss_ratio: The target loss ratio to adjust.
        tau_1: Time period (in days) for computing historical surplus and loss-to-exposure.
            Defaults to 90 days.
        tau_2: Time period (in days) for computing expected exposure. This is the period
            over which the deficit is expected to be recovered. Defaults to 90 days.
        lower_bound: Lower bound for the adjusted target loss to exposure ratio.
            Defaults to 0.0.
        upper_bound: Upper bound for the adjusted target loss to exposure ratio.
            Defaults to 1.0.
        pct_trend: Percentage trend for the expected exposure. Defaults to 1.0.
        consider_active_policies: Whether to consider active policies in the computation.
            Defaults to True.

    Returns:
        A tuple containing:
        - The adjusted target loss to exposure ratio (as percentage)
        - The adjusted target loss ratio (as percentage)
    """
    # Create the ensuro accessors
    create_ensuro_accessors()

    # Compute the surplus over the last tau_1 days
    mask = (data.expiration < today()) & (data.expiration >= today() - tau_1 * constants.day)
    historical_loss_to_exposure = data.loc[mask].loss_to_exposure.current_value(post_mortem=True) / 100
    # Compute the surplus
    historical_surplus = data.loc[mask, "pure_premium"].sum() - data.loc[mask, "actual_payout"].sum()

    if consider_active_policies:
        # Estimate the surplus for the active policies
        historical_surplus += (
            data.loc[data.expired_on.isna(), "pure_premium"].sum()
            - data.loc[data.expired_on.isna(), "payout"].sum() * historical_loss_to_exposure
        )

    target_loss_to_exposure = historical_loss_to_exposure / target_loss_ratio

    if historical_surplus >= 0:
        # If the performance is positive, simply return the target loss ratio
        return target_loss_to_exposure * 100, target_loss_ratio * 100

    else:
        historical_surplus *= -1

    # Compute the expected exposure that will be received in the next tau_2 days;
    # at the moment, this is set = the pure premium of the last tau_2 days
    mask = data.start >= today() - tau_2 * constants.day
    expected_exposure = data.loc[mask, "payout"].sum() * pct_trend

    # We want the pure premium collected with the next tau_2 days to be enough to cover:
    # 1. the expected loss +
    # 2. the historical surplus lost in the last tau_1 days

    target_loss_to_exposure = (
        historical_loss_to_exposure / target_loss_ratio
    )  # This is the target loss to exposure
    # ratio without the deficit
    extra_loss_to_exposure = (
        historical_surplus / expected_exposure
    )  # This is the extra loss to exposure ratio

    # The target loss to exposure ratio is adjusted by the extra loss to exposure ratio
    adjusted_target_loss_to_exposure = target_loss_to_exposure + extra_loss_to_exposure

    # Bound between lower_bound and upper_bound
    adjusted_target_loss_to_exposure = np.clip(adjusted_target_loss_to_exposure, lower_bound, upper_bound)

    # Compute the adjusted target loss ratio
    adjusted_target_loss_ratio = historical_loss_to_exposure / adjusted_target_loss_to_exposure

    return adjusted_target_loss_to_exposure * 100, adjusted_target_loss_ratio * 100


@dataclass
class PortfolioReview:
    """A class for reviewing and analyzing a portfolio of insurance policies.

    This class provides functionality to analyze insurance policy portfolios, including
    computing various metrics and generating reports.

    Attributes:
        data: DataFrame containing the policies data.
        split_on: List of columns to split the portfolio analysis on.
    """

    data: pd.DataFrame
    split_on: list[str]

    @classmethod
    def from_data(
        cls,
        data: pd.DataFrame,
        split_on: str | list[str] = ["rm_name"],
        validate_columns: list[str] | None = None,
    ) -> "PortfolioReview":
        """Create a PortfolioReview object from a dataframe.

        Args:
            data: DataFrame containing the policies data.
            split_on: Column or list of columns to split the portfolio analysis on.
                Defaults to ["rm_name"].
            validate_columns: Optional list of additional columns to validate in the data.
                Standard portfolio columns are validated by default.

        Returns:
            A new PortfolioReview instance.

        Raises:
            AssertionError: If required columns are missing from the data.
        """
        cls._validate_data(data, cols=validate_columns)
        if isinstance(split_on, str):
            split_on = [split_on]

        create_ensuro_accessors()

        return cls(
            data=data,
            split_on=split_on,
        )

    @staticmethod
    def _validate_data(data: pd.DataFrame, cols: list[str] | None = None) -> None:
        """Validate the required columns are present in the data.

        Args:
            data: DataFrame to validate.
            cols: Optional list of additional columns to validate.

        Raises:
            AssertionError: If any required column is missing.
        """
        assert "expired_on" in data.columns, "expired_on column is required"
        assert "start" in data.columns, "start column is required"
        assert "expiration" in data.columns, "expiration column is required"
        assert "pure_premium" in data.columns, "pure_premium column is required"
        assert "payout" in data.columns, "payout column is required"
        assert "actual_payout" in data.columns, "actual_payout column is required"

        if cols is not None:
            for col in cols:
                assert col in data.columns, f"{col} column is required"

    def review(
        self,
        show_first_date: bool = True,
        show_predicted_loss_to_exposure: bool = True,
        show_current_portfolio_pct: bool = True,
        average_duration: str | None = None,
        var_levels: float | int | list[float] | list[int] | None = None,
        **kwargs,
    ) -> "_CompiledReview":
        """Compute and generate a portfolio review.

        Args:
            show_first_date: Whether to include the first date in the review.
                Defaults to True.
            show_predicted_loss_to_exposure: Whether to include predicted loss to exposure.
                Defaults to True.
            show_current_portfolio_pct: Whether to include current portfolio percentages.
                Defaults to True.
            average_duration: Type of average duration to show. If "expected", shows
                expected average duration. If "actual", shows actual average duration.
                If None, duration is not shown. Defaults to None.
            var_levels: VaR levels to compute. Can be a single level or list of levels.
                Defaults to None.
            **kwargs: Additional keyword arguments passed to the review computation.

        Returns:
            A _CompiledReview object containing the review results.

        Raises:
            ValueError: If average_duration is not one of ["expected", "actual", None].
        """
        columns = [
            "first_date",
            "pred_loss_to_exposure",
            "loss_to_exposure",
            "loss_ratio",
            "volume",
            "current_pct",
            "average_duration",
            "target-loss-to-exposure",
            "target-loss-ratio",
        ]

        if average_duration is not None:
            if average_duration not in ["expected", "actual"]:
                raise ValueError("average_duration should be 'expected', 'actual', or None")
            elif average_duration == "expected":
                self.data["duration"] = (self.data.expiration - self.data.start).dt.days
            elif average_duration == "actual":
                self.data["duration"] = (self.data.expired_on - self.data.start).dt.days

        if show_current_portfolio_pct is True:
            total_exposure = self.data.exposure.current_value()

        grouped_data = self.data.groupby(self.split_on)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            result = {
                "loss_to_exposure": grouped_data.apply(
                    lambda x: x.loss_to_exposure.current_value(post_mortem=True)
                ),
                "loss_ratio": grouped_data.apply(lambda x: x.loss_ratio.current_value(post_mortem=True)),
                "volume": grouped_data.apply(lambda x: (x.expiration <= today()).sum()),
            }
        if show_first_date is True:
            result["first_date"] = grouped_data.start.min().dt.date
        else:
            columns.remove("first_date")

        if show_current_portfolio_pct is True:
            result["current_pct"] = (
                grouped_data.apply(lambda x: x.exposure.current_value()) / total_exposure * 100
            )
        else:
            columns.remove("current_pct")

        if show_predicted_loss_to_exposure is True:
            result["pred_loss_to_exposure"] = grouped_data.apply(
                lambda x: x.pure_premium.sum() / x.payout.sum() * 100
            )
        else:
            columns.remove("pred_loss_to_exposure")

        if average_duration is not None:
            result["average_duration"] = grouped_data.duration.mean()
        else:
            columns.remove("average_duration")

        if "target_loss_ratio" in kwargs:
            target_lr_lte = grouped_data.apply(
                lambda x: pd.Series(compute_adjusted_target_loss_ratio(x, **kwargs["target_loss_ratio"]))
            )
            result["target-loss-to-exposure"] = target_lr_lte[0]
            result["target-loss-ratio"] = target_lr_lte[1]

        else:
            columns.remove("target-loss-to-exposure")
            columns.remove("target-loss-ratio")

        if var_levels is not None:
            if isinstance(var_levels, float | int):
                var_levels = [var_levels]
            var_df = grouped_data.apply(lambda x: pd.Series(_get_var(x, var_levels, **kwargs)) * 100)
            for i, level in enumerate(var_levels):
                result[f"VaR_{level}"] = var_df[i]
                columns.append(f"VaR_{level}")

        # Put the results in a single dataframe
        results = pd.DataFrame(result)[columns]
        results.sort_index(inplace=True)

        return _CompiledReview(results)


@dataclass
class _CompiledReview:
    """A class for compiling and representing portfolio review results.

    This class provides methods to access and format the results of a portfolio review.

    Attributes:
        portfolio_review: DataFrame containing the results of the portfolio review.
    """

    portfolio_review: pd.DataFrame

    def to_df(self) -> pd.DataFrame:
        """Get a copy of the portfolio review results as a DataFrame.

        Returns:
            A copy of the portfolio review results.
        """
        return self.portfolio_review.copy()

    def to_string(self, **kwargs) -> str:
        """Convert the portfolio review results to a string representation.

        Args:
            **kwargs: Additional keyword arguments passed to pandas' to_string method.

        Returns:
            A string representation of the portfolio review results.
        """
        return self.portfolio_review.to_string(float_format="{:,.2f}%".format, **kwargs)

    def print(self, **kwargs) -> None:
        """Print the portfolio review results.

        Args:
            **kwargs: Additional keyword arguments passed to to_string method.
        """
        print(self.to_string(**kwargs))
