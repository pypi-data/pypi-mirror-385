"""Utilities for fetching data from Ensuro's API.

This module provides functionality to interact with Ensuro's API, including:
- Low-level API calls with pagination support
- High-level data retrieval methods
- Policy data processing and transformation
- Risk module data handling
"""

from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yaml

from ensuro_analytics.download import get_from_quote

RISK_MODULES_API_ADDRESS = "https://offchain-v2.ensuro.co/api/riskmodules/"


class OffchainAPI:
    """Client for interacting with Ensuro's offchain API.

    This class provides both low-level primitives for direct API calls and high-level
    methods for combining multiple calls. It handles authentication, pagination, and
    data transformation.

    Args:
        url: Base URL for the API.
        page_size: Number of results per page for pagination. Defaults to 1000.
        private_key: Optional authentication token for private data access.
    """

    def __init__(self, url: str, page_size: int = 1000, private_key: str | None = None):
        self.url = url.strip("/")
        self.page_size = page_size
        self.private_key = private_key
        self.session = requests.Session()
        if private_key:
            self.session.headers.update({"Authorization": f"Token {private_key}"})

    def __repr__(self) -> str:
        """Return a string representation of the API client."""
        return f"<OffchainAPI url={self.url}>"

    def url_to_endpoint(self, url: str) -> str:
        """Convert a full URL to an endpoint path.

        Args:
            url: Full URL including the base API URL.

        Returns:
            The endpoint path without the base URL.
        """
        if url.startswith(self.url):
            url = url[len(self.url) :]
        return url.strip("/")

    def endpoint_url(self, endpoint: str) -> str:
        """Generate a full URL for an endpoint.

        Args:
            endpoint: The endpoint path.

        Returns:
            The complete URL for the endpoint.
        """
        if endpoint.startswith(self.url):
            endpoint = endpoint[len(self.url) :]
        return f"{self.url}/{endpoint.strip('/')}/"

    def get(
        self, endpoint: str, query_params: dict | None = None, validate_response: bool = True
    ) -> requests.Response:
        """Make a GET request to the specified endpoint.

        Args:
            endpoint: The endpoint path.
            query_params: Optional query parameters to include in the request.
            validate_response: Whether to raise an exception for non-200 responses.

        Returns:
            The response from the API.

        Raises:
            requests.exceptions.HTTPError: If validate_response is True and the
                response status code is not 200.
        """
        response = self.session.get(self.endpoint_url(endpoint), params=query_params)
        if validate_response:
            response.raise_for_status()
        return response

    def multi_page_get(self, endpoint: str, query_params: dict | None = None) -> list:
        """Retrieve all pages of results from an endpoint.

        Args:
            endpoint: The endpoint path.
            query_params: Optional query parameters to include in the request.

        Returns:
            A list containing all results from all pages.

        Raises:
            requests.exceptions.HTTPError: If any response has a non-200 status code.
        """
        url = self.endpoint_url(endpoint) + f"?limit={self.page_size}"
        if query_params:
            url += "&" + "&".join([f"{k}={v}" for k, v in query_params.items()])

        results = []
        while url is not None:
            response = self.session.get(url)
            response.raise_for_status()
            results += response.json()["results"]
            url = response.json()["next"]

        return results

    def get_policies(self) -> list:
        """Retrieve all policies from the API.

        This method handles pagination and authentication for private data access.

        Returns:
            A list of all policy records.

        Raises:
            requests.exceptions.HTTPError: If any response has a non-200 status code.
        """
        policies = []
        url = self.endpoint_url("portfolio") + f"?limit={self.page_size}"
        if self.private_key is not None:
            url += "&private_data=True"

        while url is not None:
            response = self.session.get(url)
            response.raise_for_status()
            policies += response.json()["results"]
            url = response.json()["next"]

        return policies

    @staticmethod
    def get_expiration_date(row: dict, version: str = "v2") -> pd.Timestamp | float:
        """Compute the actual expiration date for a policy.

        Args:
            row: Policy data as received from the API.
            version: API version ("v1" or "v2"). Defaults to "v2".

        Returns:
            The actual expiration date as a timestamp, or np.nan if not found.

        Raises:
            ValueError: If version is not "v1" or "v2".
        """
        if version == "v1":
            colname = "tx"
        elif version == "v2":
            colname = "event"
        else:
            raise ValueError

        transactions_list = row[f"{colname}s"]
        for transaction in transactions_list:
            if transaction[f"{colname}_type"] == "resolution":
                return transaction["timestamp"]
        return np.nan

    def build_policies_table(self, quote_columns: str | Path | None = None) -> pd.DataFrame:
        """Download and transform policy data into a standardized format.

        This method retrieves policy data from the API and processes it into a
        standardized DataFrame format, including:
        - Numeric type conversion
        - Date handling and timezone normalization
        - Progress and duration calculations
        - Risk module and partner information mapping

        Args:
            quote_columns: Optional path to a YAML file containing quote column mappings.

        Returns:
            A DataFrame containing processed policy data with standardized columns.

        Raises:
            requests.exceptions.HTTPError: If API requests fail.
            yaml.YAMLError: If quote_columns file is invalid YAML.
        """
        # Get Policies Data
        policies = self.get_policies()
        # create dataset
        df = pd.DataFrame.from_records(policies).fillna(np.nan)
        to_numeric = [
            "payout",
            "premium",
            "jr_scr",
            "sr_scr",
            "loss_prob",
            "pure_premium",
            "ensuro_commission",
            "partner_commission",
            "jr_coc",
            "sr_coc",
            "actual_payout",
        ]
        df[to_numeric] = df[to_numeric].astype(float)

        # Transform data
        now = pd.to_datetime("today")

        expiration_dates = [self.get_expiration_date(row, version="v2") for row in policies]
        df["expired_on"] = expiration_dates
        df.loc[df.actual_payout == 0, "expired_on"] = df.loc[df.actual_payout == 0, "expiration"].values

        # format dates
        df["start"] = pd.to_datetime(df.start).dt.tz_localize(None)
        df["expiration"] = pd.to_datetime(df.expiration).dt.tz_localize(None)
        df["expired_on"] = pd.to_datetime(df.expired_on).dt.tz_localize(None)
        df["active"] = df.actual_payout.apply(np.isnan)

        df["progress"] = (now - df.start).apply(lambda x: np.timedelta64(x) / np.timedelta64(1, "s"))
        df["progress"] = df["progress"] / (df.expiration - df.start).apply(
            lambda x: np.timedelta64(x) / np.timedelta64(1, "s")
        )
        df.loc[~df.active, "progress"] = 1.0

        df["duration_expected"] = (df.expiration - df.start).apply(lambda x: x / np.timedelta64(1, "D"))
        df["duration_actual"] = (df.expired_on - df.start).apply(lambda x: x / np.timedelta64(1, "D"))

        # create risk module
        df["risk_module"] = df["rm"].apply(lambda x: x.split("/")[-2])

        df["partner"] = [get_from_quote(x, "partnerName") for x in df.quote]
        df["ttype"] = [get_from_quote(x, "ticketType") for x in df.quote]

        if quote_columns is not None:
            # Create columns out of quote
            with open(quote_columns, "r") as f:
                quote_columns_dict = yaml.safe_load(f)

            for key, columns in quote_columns_dict.items():
                for column in columns:
                    df[column] = [get_from_quote(x, column) for x in df.quote]

        df["start_date"] = pd.to_datetime(df.start).dt.date

        risk_modules = requests.get(RISK_MODULES_API_ADDRESS)
        risk_modules = risk_modules.json()
        risk_modules = dict(zip([x["address"] for x in risk_modules], [x["name"] for x in risk_modules]))

        df["rm_name"] = df.risk_module.map(risk_modules)

        df["start_date"] = pd.to_datetime(df["start_date"])
        df["date_price_applied"] = (
            df.groupby(["rm_name", "loss_prob"]).start.transform("min").apply(lambda x: str(x.date()))
        )

        return df
