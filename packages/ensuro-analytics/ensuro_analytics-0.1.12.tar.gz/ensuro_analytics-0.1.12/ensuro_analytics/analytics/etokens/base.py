"""Base functionality for eToken analytics.

This module provides core functionality for eToken analytics, including time unit handling,
market data retrieval, and data transformation utilities. It includes functions for:
- Time unit conversions and calculations
- Risk-free rate and market data retrieval
- eToken data processing and transformation
- LP (Liquidity Provider) data handling
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from environs import Env

env = Env()
env.read_env()

API_V2_URL = env.str("API_V2_URL", "https://offchain-v2.ensuro.co/api/")
LPS_URL = env.str("ETOKEN_URL", API_V2_URL + "lpevents/")


@dataclass
class Today:
    """Handles current date operations and formatting.

    This class provides methods to work with the current date, including:
    - Getting the current date as a normalized timestamp
    - Converting the date to string format
    - Calculating dates relative to today
    """

    @property
    def date(self):
        """Get the current date as a normalized timestamp."""
        return pd.Timestamp("today").normalize()

    @property
    def str(self):
        """Get the current date as a formatted string (YYYY-MM-DD)."""
        return self.date.strftime("%Y-%m-%d")

    def back(self, days: int):
        """Calculate a date relative to today.

        Args:
            days: Number of days to go back from today.

        Returns:
            A string representing the calculated date in YYYY-MM-DD format.
        """
        return (self.date - pd.Timedelta(days=days)).date().strftime("%Y-%m-%d")


today = Today()


@dataclass
class TimeUnits:
    """Handles time unit conversions and calculations.

    This class provides functionality for working with different time units (daily, weekly,
    monthly, yearly) and their conversions. It supports:
    - Unit validation
    - Conversion between different time units
    - Calculation of units in a year
    - Calculation of days in a unit
    - Generation of appropriate frequency strings

    Args:
        unit: Time unit string (e.g., "1D", "1W", "1M", "1Y").
    """

    unit: str

    def __post_init__(self):
        """Validate the time unit after initialization."""
        assert self.unit in ["1D", "1W", "1M", "1Y"], "Invalid unit"

    @property
    def n_units_in_one_year(self):
        """Calculate the number of units in one year.

        Returns:
            The number of units (e.g., 365 for daily, 52.14 for weekly).
        """
        match self.unit:
            case "1D":
                return 365
            case "1W":
                return 52.14
            case "1M":
                return 12.17
            case "1Y":
                return 1
            case _:
                return 0

    @property
    def n_days_in_unit(self):
        """Calculate the number of days in one unit.

        Returns:
            The number of days (e.g., 1 for daily, 7 for weekly).
        """
        match self.unit:
            case "1D":
                return 1
            case "1W":
                return 7
            case "1M":
                return 30
            case "1Y":
                return 365
            case _:
                return 0

    @property
    def daily_freq(self):
        """Get the frequency string for daily resampling.

        Returns:
            A string representing the frequency (e.g., "1D", "7D", "30D", "365D").
        """
        match self.unit:
            case "1D":
                return "1D"
            case "1W":
                return "7D"
            case "1M":
                return "30D"
            case "1Y":
                return "365D"
            case _:
                return "1D"


@lru_cache
def risk_free_rate(
    start_date: str | pd.Timestamp = today.back(365),
    end_date: str | pd.Timestamp = today.str,
) -> float:
    """Get the risk-free rate from treasury bills.

    This function retrieves the risk-free rate using 3-month treasury bill data from Yahoo Finance.
    The rate is calculated as the mean of the daily opening rates over the specified period.

    Args:
        start_date: Start date for the risk-free rate calculation. Defaults to 365 days ago.
        end_date: End date for the risk-free rate calculation. Defaults to today.

    Returns:
        The average risk-free rate as a decimal (e.g., 0.05 for 5%).
    """
    if isinstance(start_date, pd.Timestamp):
        start_date = start_date.strftime("%Y-%m-%d")

    if isinstance(end_date, pd.Timestamp):
        end_date = end_date.strftime("%Y-%m-%d")

    # Download the 3-month treasury bills
    risk_free_rate = yf.download("^IRX", start=start_date, end=end_date)
    risk_free_rate.columns = risk_free_rate.columns.get_level_values(0)
    risk_free_rate.columns.name = None
    risk_free_rate = risk_free_rate.reset_index()["Open"].mean() / 100

    return risk_free_rate


@lru_cache
def get_market_data(
    start_date: str = today.back(3650),
    end_date: str = today.str,
    ticker: str = "^GSPC",
) -> pd.DataFrame:
    """Get market data from Yahoo Finance.

    This function retrieves market data (e.g., S&P 500) from Yahoo Finance and formats it
    for use in analytics. The data is normalized to UTC timezone and includes closing prices.

    Args:
        start_date: Start date for the market data. Defaults to 10 years ago.
        end_date: End date for the market data. Defaults to today.
        ticker: The market index ticker. Defaults to "^GSPC" (S&P 500).

    Returns:
        A DataFrame containing market data with dates as index and closing prices.
    """
    # Download the S&P500 data
    df = yf.download(ticker, start=start_date, end=end_date).reset_index()
    df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df["Date"] = df["Date"].dt.tz_localize("UTC").dt.normalize()
    df.rename(columns={"Close": "close", "Date": "date"}, inplace=True)
    df.set_index("date", inplace=True)

    return df[["close"]]


def get_market_returns(
    dates=None,
    ticker: str = "^GSPC",
    start_date: str = None,
    end_date: str = None,
    freq: str = "1W",
) -> pd.DataFrame:
    """Get market returns data.

    This function retrieves and processes market returns data, either matching it with
    provided dates or generating a new time series based on start/end dates and frequency.

    Args:
        dates: List of dates to match market data with. If provided, market data will be
            aligned with these dates.
        ticker: The market index ticker. Defaults to "^GSPC" (S&P 500).
        start_date: Start date for generating market returns. Required if dates not provided.
        end_date: End date for generating market returns. Required if dates not provided.
        freq: Frequency for the market returns. Defaults to "1W" (weekly).

    Returns:
        A DataFrame containing market returns data with dates and returns.

    Raises:
        ValueError: If neither dates nor (start_date, end_date) are provided.
    """
    market_data = get_market_data(ticker=ticker)

    # Match the market data with the eToken data, in terms of dates
    # In the market data some dates may be missing due to weekends or holidays
    market_data = _match_market_etoken_dates(dates, start_date, end_date, freq, market_data)

    return market_data[["date", "returns_sp"]]


def _match_market_etoken_dates(dates, start_date, end_date, freq, market_data):
    """Match market data dates with eToken dates.

    This helper function aligns market data dates with eToken dates, handling missing
    market data due to weekends or holidays by shifting dates as needed.

    Args:
        dates: List of dates to match market data with.
        start_date: Start date for generating market returns.
        end_date: End date for generating market returns.
        freq: Frequency for the market returns.
        market_data: DataFrame containing market data.

    Returns:
        A DataFrame containing aligned market data with returns.
    """
    if dates is not None:
        market_dates = pd.Series(dates)
        market_mask = ~market_dates.isin(market_data.index)
        max_shift = 0
        n_shift = market_mask.sum()
        while market_mask.any():
            market_dates.loc[market_mask] = market_dates.loc[market_mask] - pd.Timedelta(days=1)
            market_mask = ~market_dates.isin(market_data.index)
            max_shift += 1
        if max_shift > 0:
            print(f"Shifted {n_shift} market data entries up to {max_shift} days to match the eToken data.")
        market_data = market_data.loc[market_dates]
        market_data["returns_sp"] = market_data["close"].pct_change()
        market_data.index = dates
        market_data.reset_index(inplace=True)

    elif start_date is not None and end_date is not None:
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        market_data = market_data.loc[dates]

        market_data["returns_sp"] = market_data["close"].pct_change()
        market_data.reset_index(inplace=True)

    else:
        raise ValueError("Either dates or start_date and end_date must be provided.")
    return market_data


@lru_cache
def market_returns(
    start_date: str = today.back(365),
    end_date: str = today.str,
    time_resolution: str | TimeUnits = "1W",
    ticker: str = "^GSPC",
) -> pd.DataFrame:
    """Prepare market returns data for use in metrics.

    This function retrieves and processes market returns data at the specified time
    resolution, including proper resampling and return calculation.

    Args:
        start_date: Start date for the market returns. Defaults to 365 days ago.
        end_date: End date for the market returns. Defaults to today.
        time_resolution: Time resolution for the returns. Can be a string (e.g., "1D")
            or TimeUnits object. Defaults to "1W" (weekly).
        ticker: The market index ticker. Defaults to "^GSPC" (S&P 500).

    Returns:
        A DataFrame containing market returns data with dates and returns.
    """
    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    start_date = (pd.Timestamp(start_date) - pd.Timedelta(days=365)).strftime("%Y-%m-%d")

    # Download the S&P500 data
    sp_df = yf.download(ticker, start=start_date, end=end_date).reset_index()
    sp_df.columns = sp_df.columns.get_level_values(0)
    sp_df.columns.name = None
    sp_df["Date"] = sp_df["Date"].dt.tz_localize("UTC").dt.normalize()
    sp_df.rename(columns={"Close": "close", "Date": "date"}, inplace=True)
    sp_df.set_index("date", inplace=True)

    sp_df = sp_df.resample(time_resolution.daily_freq).agg({"close": "last"})
    sp_df["returns_sp"] = sp_df["close"].pct_change()

    # Drop the last date (may have incomplete data)
    sp_df = sp_df.iloc[:-1]
    sp_df.reset_index(inplace=True)

    return sp_df[["date", "returns_sp"]]


def get_lps() -> pd.DataFrame:
    """Get Liquidity Provider (LP) data from the API.

    This function retrieves all LP data from the API, handling pagination automatically.

    Returns:
        A DataFrame containing LP data with all available fields.
    """
    session = requests.Session()
    lps_list = []
    url = LPS_URL
    while True:
        response = session.get(url)
        lps_list += response.json()["results"]
        if response.json()["next"] is None:
            break
        url = response.json()["next"]

    return pd.json_normalize(lps_list, sep="_")


def blocks_shots_to_token_metrics(
    etoken_blocks: pd.DataFrame,
    lps_df: pd.DataFrame,
    etokens_api_query: list[dict],
) -> pd.DataFrame:
    """Transform eToken blocks shots and LP data into daily metrics.

    This function processes raw eToken blocks shots and LP data to create a DataFrame with
    daily resolution and all necessary columns for analysis, including:
    - Total supply and SCR tracking
    - Deposit and withdrawal flows
    - Dividend calculations
    - Proper date handling and indexing

    Args:
        etoken_blocks: DataFrame containing eToken blocks shots data.
        lps_df: DataFrame containing LP data.
        etokens_api_query: List of dictionaries containing eToken API query results.

    Returns:
        A DataFrame containing processed eToken metrics with a multi-index of eToken and date.
    """
    # Transform the eToken blocks shots columns with correct types
    etoken_blocks["total_supply"] = etoken_blocks.total_supply.astype(float)
    etoken_blocks["scr"] = etoken_blocks.scr.astype(float)
    etoken_blocks["date"] = pd.to_datetime(etoken_blocks["date"], utc=True).dt.normalize()

    # Transform the LPs data columns with correct types
    lps_df.event_tx_timestamp = pd.to_datetime(lps_df.event_tx_timestamp)
    lps_df["date"] = lps_df.event_tx_timestamp.dt.normalize()

    # Compute the deposits and withdrawals
    lps_df["deposit"] = (lps_df.event_type == "deposit").astype(int) * lps_df.amount.astype(float)
    lps_df["withdraw"] = (lps_df.event_type == "withdraw").astype(int) * lps_df.amount.astype(float)

    # Get the eToken address and the eToken URL
    etokens_url_address_map = {r["url"]: r["address"] for r in etokens_api_query}

    # Transform the eToken URL to the eToken address
    lps_df["e_token"] = lps_df.e_token.map(etokens_url_address_map)

    # Compute the daily token balance
    daily_token_balance = (
        etoken_blocks.sort_values(["e_token", "date"])
        .groupby(["e_token", "date"])
        .agg(
            {
                "total_supply": "last",
                "scr": "last",
            }
        )
    )

    # Set a multiindex from the eToken address and the date
    e_tokens = daily_token_balance.reset_index().e_token.unique()
    dates = daily_token_balance.reset_index().date.unique()

    # Don't consider the very last date (may have incomplete data)
    dates = pd.date_range(start=dates.min(), end=dates.max(), freq="D")[:-1]

    # Set the multiindex
    reindex = pd.MultiIndex.from_product([e_tokens, dates], names=["e_token", "date"])
    daily_token_balance = daily_token_balance.reindex(reindex)

    # Fill the missing values of total supply and SCR with the last available value
    daily_token_balance = daily_token_balance.groupby(level="e_token").transform(lambda x: x.bfill().ffill())

    # Compute daily deposits and withdrawals and fill the missing values with 0
    daily_token_balance["deposit"] = lps_df.groupby(["e_token", "date"]).deposit.sum()
    daily_token_balance["withdraw"] = lps_df.groupby(["e_token", "date"]).withdraw.sum()
    daily_token_balance[["withdraw", "deposit"]] = daily_token_balance[["withdraw", "deposit"]].fillna(0)

    # Compute dividends; The dividends are computed as the difference between the total supply of the eToken
    # at time t+1 and t, minus the deposits and plus the withdrawals.
    daily_token_balance["dividend"] = (
        daily_token_balance.groupby(level="e_token").total_supply.diff()
        - daily_token_balance.deposit
        + daily_token_balance.withdraw
    )

    return daily_token_balance


def returns_dataframe(etokens_data: pd.DataFrame, time_resolution: str = "1D") -> pd.DataFrame:
    """Compute returns and related metrics for eTokens.

    This function calculates various metrics for eTokens including:
    - Returns (both nominal and perfect)
    - Utilization rate
    - Flow metrics (nominal and perfect)
    - Outlay and proceeds

    Args:
        etokens_data: DataFrame containing eToken data with total supply, deposits,
            withdrawals, SCR, and dividends.
        time_resolution: Time resolution for the returns. Defaults to "1D" (daily).

    Returns:
        A DataFrame containing all computed metrics with a multi-index of eToken and date.
    """
    if isinstance(time_resolution, str):
        time_resolution = TimeUnits(time_resolution)

    _aggregation_funcs = {
        "total_supply": "last",
        "scr": "last",
        "dividend": "sum",
        "deposit": "sum",
    }

    # Resample with desired time resolution
    returns = (
        etokens_data.reset_index(level="e_token")
        .groupby("e_token")
        .resample(time_resolution.daily_freq)
        .agg(_aggregation_funcs)
    )

    # Compute the returns
    returns["returns"] = (
        returns["dividend"] / returns.groupby(level="e_token").total_supply.shift()
    ).replace(np.inf, np.nan)
    returns["perfect_returns"] = (
        returns["dividend"] / returns.groupby(level="e_token").scr.shift()
    ).replace(np.inf, np.nan)

    # Compute the utilization rate
    returns["UR"] = returns["scr"] / returns["total_supply"]

    # Compute the flow
    returns["flow"] = returns["total_supply"].groupby(level="e_token").diff(1) - returns["dividend"]
    returns["perfect_flow"] = returns["scr"].groupby(level="e_token").diff(1)

    # Fill the first occurrence with the total supply (or SCR)
    first_occurrences = returns.groupby(level="e_token").cumcount() == 0
    returns.loc[first_occurrences, "flow"] = returns.loc[first_occurrences, "total_supply"]
    returns.loc[first_occurrences, "perfect_flow"] = returns.loc[first_occurrences, "scr"]

    # Compute the cumulative flow
    returns["cumflow"] = returns["flow"].cumsum()
    returns["perfect_cumflow"] = returns["perfect_flow"].cumsum()

    # Compute the outlay and proceeds
    returns["outlay"] = returns["flow"].apply(lambda x: 0 if x < 0 else x)
    returns["proceeds"] = -returns["flow"].apply(lambda x: 0 if x > 0 else x)
    returns["perfect_outlay"] = returns["perfect_flow"].apply(lambda x: 0 if x < 0 else x)
    returns["perfect_proceeds"] = -returns["perfect_flow"].apply(lambda x: 0 if x > 0 else x)

    # Drop the last aggregate date (may have incomplete data)
    dates = returns.index.levels[1]
    returns = returns.loc[(slice(None), dates[:-1]), :]

    return returns


def filter_first_nonzero(group: pd.DataFrame, column="deposit") -> pd.DataFrame:
    """Filter the first occurrence of a column with a nonzero value.

    Args:
        group: DataFrame group to filter.
        column: Column to check for nonzero values. Defaults to "deposit".

    Returns:
        A DataFrame containing only the rows after the first nonzero value.
    """
    nonzero_index = group.reset_index()[column].ne(0).idxmax() + 1

    return group.iloc[nonzero_index:]


def filter_returns_dataframe(returns: pd.DataFrame, filter_method="first_deposit") -> pd.DataFrame:
    """Filter returns DataFrame based on specified method.

    This function applies filtering to the returns DataFrame, currently supporting
    filtering to start after the first deposit.

    Args:
        returns: DataFrame containing returns data.
        filter_method: Method to use for filtering. Currently only supports "first_deposit".

    Returns:
        A filtered DataFrame containing returns data.

    Raises:
        ValueError: If the specified filter method is not implemented.
    """
    if filter_method == "first_deposit":
        # Start the time series only after the first deposit
        returns = (
            returns.groupby(level="e_token").apply(filter_first_nonzero).reset_index(level=0, drop=True)
        )
    else:
        raise ValueError(f"Filter method {filter_method} not implemented")

    return returns
