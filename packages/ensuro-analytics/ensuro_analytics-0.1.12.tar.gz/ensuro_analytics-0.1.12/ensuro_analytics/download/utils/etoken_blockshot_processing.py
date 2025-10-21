"""Utilities for processing eToken blockshot data.

This module provides functions for processing and transforming eToken blockshot data,
including policy filtering, insurance returns calculation, and data normalization.
"""

import numpy as np
import pandas as pd


def prepare_dataframe(
    policies: pd.DataFrame,
    etoken_to_risk_modules_map: dict[str, list[str]],
    etoken: str,
) -> pd.DataFrame:
    """Prepare a filtered DataFrame with necessary columns and calculations.

    This function filters policies for a specific eToken and calculates various
    time-based metrics including:
    - First and last day lengths
    - Duration calculations
    - Inverse duration seconds
    - Special handling for same-day policies

    Args:
        policies: DataFrame containing policy data.
        etoken_to_risk_modules_map: Dictionary mapping eToken addresses to risk module lists.
        etoken: The eToken address to filter for.

    Returns:
        A filtered DataFrame containing processed policy data for the specified eToken.
    """
    df_filter = policies.loc[policies.risk_module.isin(etoken_to_risk_modules_map.get(etoken, []))].copy()
    df_filter.expired_on = df_filter.expired_on.fillna(df_filter.expiration)
    df_filter["expired_on"] = np.minimum(df_filter["expired_on"], df_filter["expiration"])

    if df_filter.empty:
        return df_filter

    df_filter["len_first_day"] = (
        df_filter.start.dt.normalize() + pd.Timedelta(days=1) - df_filter["start"]
    ).dt.total_seconds()
    df_filter["len_last_day"] = (
        df_filter["expired_on"] - df_filter.expired_on.dt.normalize()
    ).dt.total_seconds()
    df_filter["len_last_day"] += (df_filter["expiration"] - df_filter["expired_on"]).dt.total_seconds()
    df_filter["len_other_day"] = 24 * 60 * 60
    df_filter["inv_duration_secs"] = 1 / (df_filter["expiration"] - df_filter["start"]).dt.total_seconds()

    # Handle cases where start date and expiration date are the same
    same_start_expiration = df_filter.start.dt.date == df_filter.expired_on.dt.date
    df_filter.loc[same_start_expiration, "len_first_day"] = 1.0
    df_filter.loc[same_start_expiration, "len_other_day"] = 0.0
    df_filter.loc[same_start_expiration, "len_last_day"] = 0.0
    df_filter.loc[same_start_expiration, "inv_duration_secs"] = 1.0

    for col in ["len_first_day", "len_last_day", "len_other_day"]:
        if col == "len_first_day":
            coeffs = df_filter["inv_duration_secs"].replace(np.inf, 1.0)
        else:
            coeffs = df_filter["inv_duration_secs"].replace(np.inf, 0.0)
        df_filter[col] = df_filter[col] * coeffs

    return df_filter


def compute_insurance_returns(
    df: pd.DataFrame,
    tranche_col: str,
    etoken: str,
    dates: list[pd.Timestamp],
) -> list[tuple[tuple[str, pd.Timestamp], float]]:
    """Calculate insurance returns for a given tranche and eToken.

    This function computes daily insurance returns by considering:
    - First day returns
    - Last day returns
    - Returns for days in between
    - Proper weighting based on day lengths

    Args:
        df: DataFrame containing policy data.
        tranche_col: Column name for the tranche returns (e.g., "sr_coc" or "jr_coc").
        etoken: The eToken address.
        dates: List of dates to compute returns for.

    Returns:
        A list of tuples containing ((etoken, date), daily_return) pairs.
    """
    results = []
    for date in dates:
        daily_return = 0
        mask_first_day = df.start.dt.date == date.date()
        mask_last_day = df.expired_on.dt.date == date.date()
        mask_other_days = (df.start.dt.date < date.date()) & (df.expired_on.dt.date > date.date())

        daily_return += (df.loc[mask_first_day, tranche_col] * df.loc[mask_first_day, "len_first_day"]).sum()
        daily_return += (df.loc[mask_last_day, tranche_col] * df.loc[mask_last_day, "len_last_day"]).sum()
        daily_return += (
            df.loc[mask_other_days, tranche_col] * df.loc[mask_other_days, "len_other_day"]
        ).sum()

        results.append(((etoken, date), daily_return))

    return results


def build_insurance_returns(
    data: pd.DataFrame,
    policies: pd.DataFrame,
    sr_etks_to_rm: dict[str, list[str]],
    jr_etks_to_rm: dict[str, list[str]],
) -> pd.DataFrame:
    """Build insurance returns for all eTokens and dates.

    This function processes insurance returns for both senior and junior tranches
    across all eTokens and dates, creating a comprehensive returns dataset.

    Args:
        data: DataFrame containing base data with dates.
        policies: DataFrame containing policy data.
        sr_etks_to_rm: Dictionary mapping senior eToken addresses to risk module lists.
        jr_etks_to_rm: Dictionary mapping junior eToken addresses to risk module lists.

    Returns:
        A DataFrame containing insurance returns with a multi-index of eToken and date.
    """
    dates = sorted(data.index.get_level_values(1).unique())
    etokens = sorted(data.index.get_level_values(0).unique())
    dates = pd.date_range(start=dates[0].normalize(), end=dates[-1].normalize(), freq="D")

    # Build the insurance returns with etokens and dates as a multi-index
    index = pd.MultiIndex.from_product([etokens, dates], names=["etoken", "date"])
    insurance_returns = pd.DataFrame(index=index, columns=["dividend_insurance"])
    insurance_returns["dividend_insurance"] = 0.0

    for etoken in etokens:
        # Returns from the senior tranche
        df_sr = prepare_dataframe(policies, sr_etks_to_rm, etoken)
        if not df_sr.empty:
            sr_returns = compute_insurance_returns(df_sr, "sr_coc", etoken, dates)
            for idx, value in sr_returns:
                insurance_returns.at[idx, "dividend_insurance"] += value

        # Returns from the junior tranche
        df_jr = prepare_dataframe(policies, jr_etks_to_rm, etoken)
        if not df_jr.empty:
            jr_returns = compute_insurance_returns(df_jr, "jr_coc", etoken, dates)
            for idx, value in jr_returns:
                insurance_returns.at[idx, "dividend_insurance"] += value

    return insurance_returns


def get_etokens_to_risk_modules_map(offchain_api) -> tuple[dict, dict[str, list[str]], dict[str, list[str]]]:
    """Get mappings between eTokens and risk modules.

    This function retrieves and processes risk module data to create mappings
    between eTokens and their associated risk modules.

    Args:
        offchain_api: An instance of OffchainAPI for making API calls.

    Returns:
        A tuple containing:
        - Dictionary of risk module details
        - Dictionary mapping senior eTokens to risk modules
        - Dictionary mapping junior eTokens to risk modules
    """
    riskmodules = dict()
    sr_etks_to_rm = dict()
    jr_etks_to_rm = dict()
    for riskmodule in offchain_api.get("riskmodules").json():
        riskmodules[riskmodule["address"]] = dict()
        riskmodules[riskmodule["address"]]["jr_etk"] = riskmodule["jr_etk"].split("/")[-2]
        riskmodules[riskmodule["address"]]["sr_etk"] = riskmodule["sr_etk"].split("/")[-2]

        if riskmodule["sr_etk"].split("/")[-2] not in sr_etks_to_rm.keys():
            sr_etks_to_rm[riskmodule["sr_etk"].split("/")[-2]] = [riskmodule["address"]]
        else:
            sr_etks_to_rm[riskmodule["sr_etk"].split("/")[-2]].append(riskmodule["address"])

        if riskmodule["jr_etk"].split("/")[-2] not in jr_etks_to_rm.keys():
            jr_etks_to_rm[riskmodule["jr_etk"].split("/")[-2]] = [riskmodule["address"]]
        else:
            jr_etks_to_rm[riskmodule["jr_etk"].split("/")[-2]].append(riskmodule["address"])

    return riskmodules, sr_etks_to_rm, jr_etks_to_rm


def blocks_shots_to_token_metrics(
    etoken_blocks: pd.DataFrame,
    lps_df: pd.DataFrame,
    etokens_api_query: list[dict],
) -> pd.DataFrame:
    """Transform eToken blockshots and LP data into daily metrics.

    This function processes raw eToken blockshots and LP data to create a DataFrame with
    daily resolution and all necessary columns for analysis, including:
    - Total supply and SCR tracking
    - Deposit and withdrawal flows
    - Dividend calculations
    - Proper date handling and indexing

    Args:
        etoken_blocks: DataFrame containing eToken blockshots data.
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
