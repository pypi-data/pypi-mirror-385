"""Utilities for downloading and processing Ensuro data from BigQuery.

This module provides functionality to interact with Google BigQuery to fetch and process
Ensuro data, including:
- Policy data retrieval and processing
- Time series data management
- eToken metrics calculation
- Data type conversion and normalization
"""

import json
from typing import Any

import pandas as pd
import pandas_gbq
import requests
from google.cloud import bigquery
from google.oauth2 import service_account

from ensuro_analytics.download.api import OffchainAPI
from ensuro_analytics.download.base import (
    DATETIME_COLUMNS,
    DEFAULT_POLICIES_TABLE_COLUMNS,
    ENSURO_API_URL,
    NUMERICAL_COLUMNS,
)
from ensuro_analytics.download.metrics import (
    active_policies,
    active_premium,
    collected_premium,
    default_percentage,
    exposure,
    junior_scr,
    loss_ratio,
    loss_to_exposure,
    n_payouts,
    payouts,
    post_mortem_premium,
    premium_balance,
    scr,
    senior_scr,
    total_policies,
)
from ensuro_analytics.download.utils import etoken_blockshot_processing as etk_processing


class MetricAccessor:
    """Accessor for a metric module bound to a BigQuery interface.

    This class wraps a metric module and provides methods that automatically
    pass the BigQuery interface as the first argument, similar to how
    pandas accessors work.
    """

    def __init__(self, bq_interface: "BigQueryInterface", module: Any):
        """Initialize the accessor.

        Args:
            bq_interface: The BigQuery interface to use for queries.
            module: The metric module (e.g., active_policies).
        """
        self._bq = bq_interface
        self._module = module
        self.__name__ = module.__name__.split(".")[-1]

    def __repr__(self) -> str:
        """String representation of the accessor."""
        return f"<MetricAccessor '{self.__name__}'>"

    def current_value(self, **kwargs) -> Any:
        """Compute the current value of the metric.

        Args:
            **kwargs: Additional arguments passed to the metric function.

        Returns:
            The current value of the metric.
        """
        return self._module.current_value(self._bq, **kwargs)

    def at_t(self, date: pd.Timestamp, **kwargs) -> Any:
        """Compute the metric at a specific point in time.

        Args:
            date: The timestamp at which to compute the metric.
            **kwargs: Additional arguments passed to the metric function.

        Returns:
            The value of the metric at the given date.
        """
        return self._module.at_t(self._bq, date, **kwargs)

    def time_series(
        self,
        freq: str = "1W",
        end_date: pd.Timestamp | None = None,
        start_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Compute a time series of the metric.

        Args:
            freq: Frequency of the time series.
            end_date: Maximum date to include.
            start_date: Minimum date to include.
            **kwargs: Additional arguments passed to the metric function.

        Returns:
            A Series containing metric values indexed by date.
        """
        return self._module.time_series(
            self._bq, freq=freq, end_date=end_date, start_date=start_date, **kwargs
        )

    def rolling_at_t(
        self, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
    ) -> Any:
        """Compute rolling window value at a specific time.

        Args:
            date: Center of the time window.
            timedelta: Half-width of the time window.
            **kwargs: Additional arguments passed to the metric function.

        Returns:
            The rolling value of the metric.

        Raises:
            AttributeError: If the metric doesn't support rolling_at_t.
        """
        if hasattr(self._module, "rolling_at_t"):
            return self._module.rolling_at_t(self._bq, date, timedelta, **kwargs)
        else:
            raise AttributeError(f"Metric '{self.__name__}' does not support rolling_at_t")


def get_risk_modules_map(url: str = "https://offchain-v2.ensuro.co/api/riskmodules/") -> dict[str, str]:
    """
    Fetches the risk modules mapping from the provided URL.
    """
    risk_modules_map = requests.get(url)
    risk_modules_map = risk_modules_map.json()
    risk_modules_map = dict(
        zip([x["address"] for x in risk_modules_map], [x["name"] for x in risk_modules_map])
    )
    return risk_modules_map


class BigQueryInterface:
    """Interface for interacting with Google BigQuery API and computing metrics.

    This class provides methods to fetch and process data from BigQuery tables,
    including policy data, time series, and eToken metrics. It also includes
    direct metric calculations through BigQuery queries.

    Attributes:
        project_id: The Google Cloud project ID.
        dataset_name: The name of the dataset in BigQuery.
        table_name: Name of the policies table in BigQuery.
        account_key_path: Optional path to the service account key file.
        policies_table_columns: List of columns to fetch from the policies table.
        credentials: Google Auth credentials for BigQuery client.
        Client: BigQuery client instance.
    """

    def __init__(
        self,
        project_id: str,
        dataset_name: str,
        account_key_path: str | None = None,
        table_name: str = "policies_quant",
        policies_table_columns: list[str] | None = None,
    ):
        """Initialize the BigQuery interface.

        Args:
            project_id: The Google Cloud project ID.
            dataset_name: The name of the dataset in BigQuery.
            account_key_path: Optional path to the service account key file.
            table_name: Name of the policies table in BigQuery.
            policies_table_columns: Optional list of columns to fetch from policies table.
        """
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.table_name = table_name
        self.account_key_path = account_key_path
        self.credentials = None
        self.filters = {}

        if self.account_key_path is not None:
            self.credentials = service_account.Credentials.from_service_account_file(self.account_key_path)

        self.Client = bigquery.Client(credentials=self.credentials, project=self.project_id)

        if policies_table_columns is None:
            self.policies_table_columns = DEFAULT_POLICIES_TABLE_COLUMNS
        else:
            self.policies_table_columns = policies_table_columns

        self._create_metric_accessors()

    def _create_metric_accessors(self):
        """Create metric accessors for dot notation access."""
        # Create metric accessors for dot notation access
        self.active_policies = MetricAccessor(self, active_policies)
        self.active_premium = MetricAccessor(self, active_premium)
        self.collected_premium = MetricAccessor(self, collected_premium)
        self.default_percentage = MetricAccessor(self, default_percentage)
        self.exposure = MetricAccessor(self, exposure)
        self.junior_scr = MetricAccessor(self, junior_scr)
        self.loss_ratio = MetricAccessor(self, loss_ratio)
        self.loss_to_exposure = MetricAccessor(self, loss_to_exposure)
        self.n_payouts = MetricAccessor(self, n_payouts)
        self.payouts = MetricAccessor(self, payouts)
        self.post_mortem_premium = MetricAccessor(self, post_mortem_premium)
        self.premium_balance = MetricAccessor(self, premium_balance)
        self.scr = MetricAccessor(self, scr)
        self.senior_scr = MetricAccessor(self, senior_scr)
        self.total_policies = MetricAccessor(self, total_policies)

    def filter(self, **kwargs) -> "BigQueryInterface":
        """Apply filters to be used in subsequent queries.

        Supports special suffixes for different operations:
        - __gt: greater than
        - __gte: greater than or equal
        - __lt: less than
        - __lte: less than or equal
        - __ne: not equal
        - __like: SQL LIKE pattern matching
        - __ilike: case-insensitive LIKE (uses LOWER)
        - __isnull: IS NULL check (value should be True/False)
        - __in: explicit IN clause (value should be a list)
        - __between: BETWEEN operation (value should be a tuple/list of 2 elements)
        - __contains: for array fields (BigQuery specific)
        - __startswith: starts with pattern
        - __endswith: ends with pattern

        Args:
            **kwargs: Key-value pairs where keys can include operators.

        Returns:
            Self for method chaining.

        Examples:
            bqi.filter(premium__gt=1000, start_date__lte='2023-12-31')
            bqi.filter(rm_name__like='Risk%', active__ne=False)
            bqi.filter(amount__between=(100, 500))
            bqi.filter(tags__contains='high-risk')
            bqi.filter(description__isnull=False)
        """
        for key, value in kwargs.items():
            # Parse special operators
            if "__" in key:
                parts = key.rsplit("__", 1)
                if len(parts) == 2 and parts[1] in [
                    "gt",
                    "gte",
                    "lt",
                    "lte",
                    "ne",
                    "like",
                    "ilike",
                    "isnull",
                    "in",
                    "between",
                    "contains",
                    "startswith",
                    "endswith",
                ]:
                    column, operator = parts
                    self.filters[key] = {"column": column, "operator": operator, "value": value}
                else:
                    # No valid operator found, treat as regular column name
                    if not isinstance(value, list):
                        value = [value]
                    self.filters[key] = value
            else:
                # Regular equals operation
                if not isinstance(value, list):
                    value = [value]
                self.filters[key] = value
        return self

    def clear_filters(self) -> None:
        """Clear all filters."""
        self.filters = {}

    @staticmethod
    def _escape_sql_string(value: str) -> str:
        """Escape SQL string to prevent injection.

        Args:
            value: String value to escape.

        Returns:
            Escaped string safe for SQL queries.
        """
        # Replace single quotes with double single quotes (SQL standard)
        return value.replace("'", "''")

    def generate_filter_clause(self, existing_where: str = "") -> str:
        """Generate SQL WHERE clause from filters.

        Args:
            existing_where: Existing WHERE clause to append filters to.

        Returns:
            Complete WHERE clause including filters.
        """
        if not self.filters:
            return existing_where

        filter_conditions = []

        for key, filter_value in self.filters.items():
            # Check if it's an advanced filter operation
            if isinstance(filter_value, dict) and "operator" in filter_value:
                column = filter_value["column"]
                operator = filter_value["operator"]
                value = filter_value["value"]

                condition = self._build_advanced_condition(column, operator, value)
                if condition:
                    filter_conditions.append(condition)
            else:
                # Regular filter (equals or IN)
                values = filter_value
                if len(values) == 1:
                    # Single value - use equals
                    value = values[0]
                    condition = self._build_equals_condition(key, value)
                else:
                    # Multiple values - use IN
                    condition = self._build_in_condition(key, values)

                if condition:
                    filter_conditions.append(condition)

        if not filter_conditions:
            return existing_where

        filter_clause = " AND ".join(filter_conditions)

        if existing_where.strip():
            # Append to existing WHERE clause
            if existing_where.strip().upper().startswith("WHERE"):
                return f"{existing_where} AND {filter_clause}"
            else:
                return f"WHERE {existing_where} AND {filter_clause}"
        else:
            # Create new WHERE clause
            return f"WHERE {filter_clause}"

    def _build_advanced_condition(self, column: str, operator: str, value: Any) -> str:
        """Build advanced filter condition based on operator.

        Args:
            column: Column name
            operator: Filter operator
            value: Filter value

        Returns:
            SQL condition string or empty string if invalid
        """
        if operator == "gt":
            return f"{column} > {self._format_value(value)}"
        elif operator == "gte":
            return f"{column} >= {self._format_value(value)}"
        elif operator == "lt":
            return f"{column} < {self._format_value(value)}"
        elif operator == "lte":
            return f"{column} <= {self._format_value(value)}"
        elif operator == "ne":
            if value is None:
                return f"{column} IS NOT NULL"
            return f"{column} != {self._format_value(value)}"
        elif operator == "like":
            return f"{column} LIKE {self._format_value(value)}"
        elif operator == "ilike":
            # BigQuery doesn't have ILIKE, use LOWER for case-insensitive
            return f"LOWER({column}) LIKE LOWER({self._format_value(value)})"
        elif operator == "isnull":
            if value:
                return f"{column} IS NULL"
            else:
                return f"{column} IS NOT NULL"
        elif operator == "in":
            if not isinstance(value, (list, tuple)):
                value = [value]
            return self._build_in_condition(column, value)
        elif operator == "between":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError(f"BETWEEN operator requires a list/tuple of 2 values, got: {value}")
            return f"{column} BETWEEN {self._format_value(value[0])} AND {self._format_value(value[1])}"
        elif operator == "contains":
            # BigQuery array contains
            return f"{self._format_value(value)} IN UNNEST({column})"
        elif operator == "startswith":
            pattern = str(value).replace("%", "\\%").replace("_", "\\_")
            return f"{column} LIKE {self._format_value(pattern + '%')}"
        elif operator == "endswith":
            pattern = str(value).replace("%", "\\%").replace("_", "\\_")
            return f"{column} LIKE {self._format_value('%' + pattern)}"
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _build_equals_condition(self, column: str, value: Any) -> str:
        """Build equals condition for a single value."""
        if value is None:
            return f"{column} IS NULL"
        return f"{column} = {self._format_value(value)}"

    def _build_in_condition(self, column: str, values: list) -> str:
        """Build IN condition for multiple values."""
        if not values:
            return ""

        # Separate NULL values
        null_values = [v for v in values if v is None]
        non_null_values = [v for v in values if v is not None]

        conditions = []

        if non_null_values:
            formatted_values = [self._format_value(v) for v in non_null_values]
            conditions.append(f"{column} IN ({', '.join(formatted_values)})")

        if null_values:
            conditions.append(f"{column} IS NULL")

        if len(conditions) > 1:
            return f"({' OR '.join(conditions)})"
        elif conditions:
            return conditions[0]
        else:
            return ""

    def _format_value(self, value: Any) -> str:
        """Format a value for SQL query."""
        if isinstance(value, str):
            return f"'{self._escape_sql_string(value)}'"
        elif isinstance(value, bool):
            return str(value).upper()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, pd.Timestamp):
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        elif value is None:
            return "NULL"
        else:
            # Convert to string and escape
            return f"'{self._escape_sql_string(str(value))}'"

    def get_active_filters(self) -> dict:
        """Get currently active filters.

        Returns:
            Dictionary of active filters.
        """
        return self.filters.copy()

    def has_filters(self) -> bool:
        """Check if any filters are active.

        Returns:
            True if filters are active, False otherwise.
        """
        return bool(self.filters)

    def remove_filter(self, key: str) -> "BigQueryInterface":
        """Remove a specific filter.

        Args:
            key: Filter key to remove.

        Returns:
            Self for method chaining.
        """
        self.filters.pop(key, None)
        return self

    # Base functionality methods (merged from BigQueryBase)
    def get_table_name(self) -> str:
        """Get the fully qualified table name."""
        return f"`{self.project_id}.{self.dataset_name}.{self.table_name}`"

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a BigQuery query using pandas-gbq.

        Args:
            query: SQL query to execute.

        Returns:
            DataFrame containing query results.
        """
        return pandas_gbq.read_gbq(
            query,
            project_id=self.project_id,
            credentials=self.credentials,
            use_bqstorage_api=True,
        )

    def _freq_to_date_trunc(self, freq: str) -> str:
        """Convert pandas frequency to BigQuery DATE_TRUNC unit."""
        mapping = {
            "D": "DAY",
            "W": "WEEK",
            "M": "MONTH",
            "Q": "QUARTER",
            "Y": "YEAR",
            "H": "HOUR",
        }
        # Extract the unit letter (last character) and numeric multiplier
        if freq.isdigit():
            return "DAY"  # Default for numeric-only frequencies

        unit = freq[-1]
        return mapping.get(unit, "DAY")

    def _freq_to_interval(self, freq: str) -> str:
        """Convert pandas frequency to BigQuery INTERVAL unit."""
        mapping = {
            "D": "DAY",
            "W": "WEEK",
            "M": "MONTH",
            "Q": "QUARTER",
            "Y": "YEAR",
            "H": "HOUR",
        }
        unit = freq[-1]

        # Handle custom frequencies like "10D"
        if len(freq) > 1 and freq[:-1].isdigit():
            multiplier = int(freq[:-1])
            return f"{multiplier} {mapping.get(unit, 'DAY')}"

        return mapping.get(unit, "DAY")

    def _format_timestamp(self, date: pd.Timestamp) -> str:
        """Format a timestamp for BigQuery queries."""
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def _generate_date_series_cte(
        self,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        freq: str,
    ) -> str:
        """Generate a CTE for date series in BigQuery."""
        interval = self._freq_to_interval(freq)
        date_trunc = self._freq_to_date_trunc(freq)

        return f"""
        date_series AS (
            SELECT DATE_TRUNC(date, {date_trunc}) as period_date
            FROM UNNEST(
                GENERATE_DATE_ARRAY(
                    DATE('{start_date.strftime('%Y-%m-%d')}'),
                    DATE('{end_date.strftime('%Y-%m-%d')}'),
                    INTERVAL {interval}
                )
            ) AS date
        )
        """

    # Original BigQueryInterface methods
    @staticmethod
    def _date_cols_to_datetime(df: pd.DataFrame, columns: list[str] = DATETIME_COLUMNS):
        """
        Converts the specified columns of the dataframe to datetime.

        Args:
            df: DataFrame containing the columns to convert.
            columns: List of column names to convert. Defaults to DATETIME_COLUMNS.

        Returns:
            DataFrame with specified columns converted to datetime format.
        """
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)
        return df

    @staticmethod
    def _bytes_to_dict(col: pd.Series) -> pd.Series:
        """Convert bytes columns to dictionaries.

        Args:
            col: Series containing bytes or JSON strings to convert.

        Returns:
            Series with bytes/JSON strings converted to dictionaries.
        """
        quote_types = col.apply(type).unique()
        if bytes in quote_types:
            col = col.apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)
            col = col.apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return col

    def sql(self, sql_query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame.

        Args:
            sql_query: The SQL query to execute.

        Returns:
            DataFrame containing the query results.
        """
        df = self.Client.query(sql_query).to_dataframe()
        return df

    def policies_table(self, limit: int | None = None) -> pd.DataFrame:
        """
        Fetches data from the policies table and returns it as a dataframe.

        Args:
            limit: Optional maximum number of rows to return.

        Returns:
            DataFrame containing processed policy data.
        """
        columns_str = ", ".join(self.policies_table_columns)
        sql_query = f"SELECT * FROM {self.get_table_name()}"
        if limit is not None:
            sql_query += f" ORDER BY id DESC LIMIT {limit}"
        sql_query = f"SELECT {columns_str} FROM ({sql_query}) ORDER BY id ASC"

        data = self._date_cols_to_datetime(self.sql(sql_query))
        data = self.format_columns_dtypes(data)
        data["quote"] = self._bytes_to_dict(data.quote)

        return data

    @staticmethod
    def format_columns_dtypes(data: pd.DataFrame) -> pd.DataFrame:
        """
        Format columns in the DataFrame to appropriate data types.
        """
        for col in NUMERICAL_COLUMNS:
            data[col] = data[col].astype(float)
        data["active"] = data["active"].astype(bool)
        return data

    def time_series_table(self) -> pd.DataFrame:
        """Fetch time series data from BigQuery.

        Returns:
            DataFrame containing processed time series data.
        """
        sql_query = f"SELECT * FROM `{self.project_id}.{self.dataset_name}.time_series`"
        return self._date_cols_to_datetime(self.sql(sql_query))

    def etoken_blockshot(self) -> pd.DataFrame:
        """Fetch eToken blockshot data from BigQuery.

        Returns:
            DataFrame containing processed eToken blockshot data.
        """
        sql_query = f"SELECT * FROM `{self.project_id}.{self.dataset_name}.etoken_block_shot_quant`"
        return self._date_cols_to_datetime(self.sql(sql_query))

    def token_metrics(self, include_insurance_returns: bool = False) -> pd.DataFrame:
        """Calculate eToken metrics with optional insurance returns.

        This function combines eToken blockshot data with LP events and API data
        to calculate comprehensive token metrics.

        Args:
            include_insurance_returns: If True, includes returns from Ensuro's
                insurance activity. If False, only includes compound returns from
                insurance activity and investments.

        Returns:
            DataFrame containing processed token metrics.
        """
        etoken_blockshot = self.etoken_blockshot()

        offchain_api = OffchainAPI(ENSURO_API_URL)

        lps = pd.json_normalize(offchain_api.multi_page_get("lpevents"), sep="_")
        etokens_api_query = offchain_api.get("etokens").json()

        token_metrics = etk_processing.blocks_shots_to_token_metrics(
            etoken_blockshot, lps, etokens_api_query
        )

        if include_insurance_returns is True:
            riskmodules, sr_etks_to_rm, jr_etks_to_rm = etk_processing.get_etokens_to_risk_modules_map(
                offchain_api
            )
            policies = self.policies_table()
            insurance_returns = etk_processing.build_insurance_returns(
                token_metrics, policies, sr_etks_to_rm, jr_etks_to_rm
            )
            token_metrics["dividend_insurance"] = insurance_returns.dividend_insurance

        return token_metrics

    def fetch_data(self, table: str) -> pd.DataFrame:
        """Fetch data from specified tables.

        Args:
            table: Name of the table to fetch data from. Must be either 'portfolio'
                or 'time-series'.

        Returns:
            DataFrame containing the fetched data.

        Raises:
            AssertionError: If the table name is not 'portfolio' or 'time-series'.
        """
        assert table in [
            "portfolio",
            "time-series",
        ], "table must be either 'portfolio' or 'time-series'"

        if table == "portfolio":
            data = self.policies_table()
        elif table == "time-series":
            data = self.time_series_table()

        return data

    # Metric calculation methods
    # Active Policies Methods
    def active_policies_current(self, **kwargs) -> int:
        """Get current active policies count."""
        return active_policies.current_value(self, **kwargs)

    def active_policies_at_t(self, date: pd.Timestamp, **kwargs) -> int:
        """Get active policies count at a specific date."""
        return active_policies.at_t(self, date, **kwargs)

    def active_policies_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get active policies time series."""
        return active_policies.time_series(
            self, freq=freq, start_date=start_date, end_date=end_date, **kwargs
        )

    # Active Premium Methods
    def active_premium_current(self, **kwargs) -> float:
        """Get current active premium value."""
        return active_premium.current_value(self, **kwargs)

    def active_premium_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get active premium value at a specific date."""
        return active_premium.at_t(self, date, **kwargs)

    def active_premium_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get active premium time series."""
        return active_premium.time_series(
            self, freq=freq, start_date=start_date, end_date=end_date, **kwargs
        )

    # Total Policies Methods
    def total_policies_current(self, post_mortem: bool = False, **kwargs) -> int:
        """Get current total policies count."""
        return total_policies.current_value(self, post_mortem=post_mortem, **kwargs)

    def total_policies_at_t(self, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> int:
        """Get total policies count at a specific date."""
        return total_policies.at_t(self, date, post_mortem=post_mortem, **kwargs)

    def total_policies_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get total policies time series."""
        return total_policies.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def total_policies_rolling_at_t(
        self, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
    ) -> int:
        """Get rolling total policies count."""
        return total_policies.rolling_at_t(self, date, timedelta=timedelta, **kwargs)

    # Loss Ratio Methods
    def loss_ratio_current(self, post_mortem: bool = False, **kwargs) -> float:
        """Get current loss ratio."""
        return loss_ratio.current_value(self, post_mortem=post_mortem, **kwargs)

    def loss_ratio_at_t(self, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
        """Get loss ratio at a specific date."""
        return loss_ratio.at_t(self, date, post_mortem=post_mortem, **kwargs)

    def loss_ratio_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        period_column: str = "expiration",
        percent: bool = False,
        **kwargs,
    ) -> pd.Series:
        """Get loss ratio time series."""
        return loss_ratio.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            start_date=start_date,
            end_date=end_date,
            period_column=period_column,
            percent=percent,
            **kwargs,
        )

    def loss_ratio_rolling_at_t(
        self, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
    ) -> float:
        """Get rolling loss ratio."""
        return loss_ratio.rolling_at_t(self, date, timedelta=timedelta, **kwargs)

    # Collected Premium Methods
    def collected_premium_current(self, **kwargs) -> float:
        """Get current collected premium value."""
        return collected_premium.current_value(self, **kwargs)

    def collected_premium_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get collected premium value at a specific date."""
        return collected_premium.at_t(self, date, **kwargs)

    def collected_premium_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get collected premium time series."""
        return collected_premium.time_series(
            self, freq=freq, start_date=start_date, end_date=end_date, **kwargs
        )

    def collected_premium_rolling_at_t(
        self, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
    ) -> float:
        """Get rolling collected premium."""
        return collected_premium.rolling_at_t(self, date, timedelta=timedelta, **kwargs)

    # Payouts Methods
    def payouts_current(self, post_mortem: bool = False, **kwargs) -> float:
        """Get current total payouts."""
        return payouts.current_value(self, post_mortem=post_mortem, **kwargs)

    def payouts_at_t(self, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
        """Get total payouts at a specific date."""
        return payouts.at_t(self, date, post_mortem=post_mortem, **kwargs)

    def payouts_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        period_column: str = "expiration",
        **kwargs,
    ) -> pd.Series:
        """Get payouts time series."""
        return payouts.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            start_date=start_date,
            end_date=end_date,
            period_column=period_column,
            **kwargs,
        )

    # Number of Payouts Methods
    def n_payouts_current(self, post_mortem: bool = False, **kwargs) -> int:
        """Get current number of payouts."""
        return n_payouts.current_value(self, post_mortem=post_mortem, **kwargs)

    def n_payouts_at_t(self, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> int:
        """Get number of payouts at a specific date."""
        return n_payouts.at_t(self, date, post_mortem=post_mortem, **kwargs)

    def n_payouts_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        period_column: str = "expiration",
        **kwargs,
    ) -> pd.Series:
        """Get number of payouts time series."""
        return n_payouts.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            start_date=start_date,
            end_date=end_date,
            period_column=period_column,
            **kwargs,
        )

    # Default Percentage Methods
    def default_percentage_current(self, post_mortem: bool = False, **kwargs) -> float:
        """Get current default percentage."""
        return default_percentage.current_value(self, post_mortem=post_mortem, **kwargs)

    def default_percentage_at_t(self, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
        """Get default percentage at a specific date."""
        return default_percentage.at_t(self, date, post_mortem=post_mortem, **kwargs)

    def default_percentage_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        period_column: str = "expiration",
        percent: bool = False,
        **kwargs,
    ) -> pd.Series:
        """Get default percentage time series."""
        return default_percentage.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            start_date=start_date,
            end_date=end_date,
            period_column=period_column,
            percent=percent,
            **kwargs,
        )

    def default_percentage_rolling_at_t(
        self, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
    ) -> float:
        """Get rolling default percentage."""
        return default_percentage.rolling_at_t(self, date, timedelta=timedelta, **kwargs)

    # SCR Methods
    def scr_current(self, **kwargs) -> float:
        """Get current total SCR."""
        return scr.current_value(self, **kwargs)

    def scr_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get total SCR at a specific date."""
        return scr.at_t(self, date, **kwargs)

    def scr_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get total SCR time series."""
        return scr.time_series(self, freq=freq, start_date=start_date, end_date=end_date, **kwargs)

    # Junior SCR Methods
    def junior_scr_current(self, **kwargs) -> float:
        """Get current junior SCR."""
        return junior_scr.current_value(self, **kwargs)

    def junior_scr_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get junior SCR at a specific date."""
        return junior_scr.at_t(self, date, **kwargs)

    def junior_scr_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get junior SCR time series."""
        return junior_scr.time_series(self, freq=freq, start_date=start_date, end_date=end_date, **kwargs)

    # Senior SCR Methods
    def senior_scr_current(self, **kwargs) -> float:
        """Get current senior SCR."""
        return senior_scr.current_value(self, **kwargs)

    def senior_scr_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get senior SCR at a specific date."""
        return senior_scr.at_t(self, date, **kwargs)

    def senior_scr_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get senior SCR time series."""
        return senior_scr.time_series(self, freq=freq, start_date=start_date, end_date=end_date, **kwargs)

    # Exposure Methods
    def exposure_current(self, **kwargs) -> float:
        """Get current total exposure."""
        return exposure.current_value(self, **kwargs)

    def exposure_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get total exposure at a specific date."""
        return exposure.at_t(self, date, **kwargs)

    def exposure_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get exposure time series."""
        return exposure.time_series(self, freq=freq, start_date=start_date, end_date=end_date, **kwargs)

    # Loss to Exposure Methods
    def loss_to_exposure_current(self, post_mortem: bool = False, **kwargs) -> float:
        """Get current loss to exposure ratio."""
        return loss_to_exposure.current_value(self, post_mortem=post_mortem, **kwargs)

    def loss_to_exposure_at_t(self, date: pd.Timestamp, post_mortem: bool = False, **kwargs) -> float:
        """Get loss to exposure ratio at a specific date."""
        return loss_to_exposure.at_t(self, date, post_mortem=post_mortem, **kwargs)

    def loss_to_exposure_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        period_column: str = "expiration",
        percent: bool = False,
        **kwargs,
    ) -> pd.Series:
        """Get loss to exposure time series."""
        return loss_to_exposure.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            start_date=start_date,
            end_date=end_date,
            period_column=period_column,
            percent=percent,
            **kwargs,
        )

    def loss_to_exposure_rolling_at_t(
        self, date: pd.Timestamp, timedelta: pd.Timedelta = pd.Timedelta(days=7), **kwargs
    ) -> float:
        """Get rolling loss to exposure ratio."""
        return loss_to_exposure.rolling_at_t(self, date, timedelta=timedelta, **kwargs)

    # Premium Balance Methods
    def premium_balance_current(
        self, post_mortem: bool = False, use_pure_premium: bool = True, **kwargs
    ) -> float:
        """Get current premium balance."""
        return premium_balance.current_value(
            self, post_mortem=post_mortem, use_pure_premium=use_pure_premium, **kwargs
        )

    def premium_balance_at_t(
        self,
        date: pd.Timestamp,
        post_mortem: bool = False,
        use_pure_premium: bool = True,
        **kwargs,
    ) -> float:
        """Get premium balance at a specific date."""
        return premium_balance.at_t(
            self,
            date,
            post_mortem=post_mortem,
            use_pure_premium=use_pure_premium,
            **kwargs,
        )

    def premium_balance_time_series(
        self,
        freq: str = "1W",
        cumulative: bool = False,
        use_pure_premium: bool = True,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        period_column: str = "expiration",
        **kwargs,
    ) -> pd.Series:
        """Get premium balance time series."""
        return premium_balance.time_series(
            self,
            freq=freq,
            cumulative=cumulative,
            use_pure_premium=use_pure_premium,
            start_date=start_date,
            end_date=end_date,
            period_column=period_column,
            **kwargs,
        )

    # Post Mortem Premium Methods
    def post_mortem_premium_current(self, **kwargs) -> float:
        """Get current post mortem premium."""
        return post_mortem_premium.current_value(self, **kwargs)

    def post_mortem_premium_at_t(self, date: pd.Timestamp, **kwargs) -> float:
        """Get post mortem premium at a specific date."""
        return post_mortem_premium.at_t(self, date, **kwargs)

    def post_mortem_premium_time_series(
        self,
        freq: str = "1W",
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
        **kwargs,
    ) -> pd.Series:
        """Get post mortem premium time series."""
        return post_mortem_premium.time_series(
            self, freq=freq, start_date=start_date, end_date=end_date, **kwargs
        )

    # Comprehensive Metrics
    def compute_aggregate_metrics(self, date: pd.Timestamp) -> dict[str, Any]:
        """Compute multiple metrics at a specific point in time.

        Args:
            date: Timestamp at which to compute the metrics.

        Returns:
            Dictionary containing various metrics.
        """
        metrics = {
            "active_premium": self.active_premium_at_t(date),
            "inactive_premium": self.collected_premium_at_t(date),
            "active_policies": self.active_policies_at_t(date),
            "total_policies": self.total_policies_at_t(date),
            "total_payouts": self.payouts_at_t(date),
            "num_payouts": self.n_payouts_at_t(date),
            "total_scr_used": self.scr_at_t(date),
            "loss_ratio": self.loss_ratio_at_t(date),
            "default_percentage": self.default_percentage_at_t(date),
            "exposure": self.exposure_at_t(date),
            "loss_to_exposure": self.loss_to_exposure_at_t(date),
            "post_mortem_premium": self.post_mortem_premium_at_t(date),
        }

        # Add rolling metrics if needed
        rolling_window = pd.Timedelta(days=7)
        metrics["rolling_loss_ratio"] = self.loss_ratio_rolling_at_t(date, timedelta=rolling_window)
        metrics["rolling_default_percentage"] = self.default_percentage_rolling_at_t(
            date, timedelta=rolling_window
        )
        metrics["rolling_n_policies"] = self.total_policies_rolling_at_t(date, timedelta=rolling_window)
        metrics["rolling_premium"] = self.collected_premium_rolling_at_t(date, timedelta=rolling_window)

        return metrics
