import re

import pandas as pd


def date_to_period(dates, freq):
    """
    Maps datetime objects in a series to period start times based on the given frequency.
    Handles both standard and custom frequencies.

    Args:
        dates (pd.Series): Series of datetime objects.
        freq (str): Frequency string, e.g., '10D' for ten-day periods or 'M' for months.

    Returns:
        pd.Series: Series of period start times.
    """
    # Regular expression pattern for standard frequency (e.g., 'M', 'Q', 'A', 'D', etc.)
    # Allows optional leading '1' (e.g., '1M', '1W', '1D', etc.)
    standard_freq_pattern = r"^(1)?[BQWYMDHSTLUN]+$"

    if re.match(standard_freq_pattern, freq):
        # Use pandas to_period for standard frequencies
        return dates.dt.to_period(freq).dt.start_time
    else:
        # Custom frequency handling
        # Extract the frequency number and unit (e.g., '10D' -> (10, 'D'))
        freq_num, freq_unit = int(freq[:-1]), freq[-1]

        # Create
        delta_in_days = pd.Timedelta(freq_num, unit=freq_unit).days

        # Calculate the number of units since a reference date (e.g., '1970-01-01')
        units_since_ref = (dates - pd.Timestamp("1970-01-01")).dt.days // delta_in_days

        # Calculate the start date of each custom period
        period_start_dates = pd.to_datetime(units_since_ref * freq_num, unit=freq_unit, origin="1970-01-01")

        return period_start_dates


def _max_date_range(data: pd.DataFrame, freq: str):
    """
    Computes the maximum date range (from the first start date to the last expiration date) for the given data and frequency.
    """
    start_dates = data.start.dt.normalize().unique()
    end_dates = data.expiration.dt.normalize().unique()

    dates = sorted(list(set(start_dates).union(set(end_dates))))
    dates = pd.Series(dates)

    return date_to_period(dates, freq).unique()
