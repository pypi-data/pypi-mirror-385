"""
This module contains the functions to download data from Ensuro's API and BigQuery.
"""

ENSURO_API_URL = "https://offchain-v2.ensuro.co/api/"


def get_from_quote(x, field):
    """
    This function attempts to retrieve a specific field from policies' metadata in the 'quote' column.

    Parameters:
    x (dict): The quote from which to retrieve the field. It is expected to be a dictionary with a "data" key.
    field (str): The name of the field to retrieve from the quote.

    Returns:
    The value of the specified field if it exists, None otherwise.
    """
    if not isinstance(x, dict):
        return None
    try:
        return x["data"][field]
    except (KeyError, TypeError):
        return None


DEFAULT_POLICIES_TABLE_COLUMNS = [
    "id",
    "ensuro_id",
    "payout",
    "loss_prob",
    "jr_scr",
    "sr_scr",
    "pure_premium",
    "ensuro_commission",
    "partner_commission",
    "jr_coc",
    "sr_coc",
    "start",
    "expiration",
    "actual_payout",
    "expired_on",
    "premium",
    "active",
    "progress",
    "duration_expected",
    "duration_actual",
    "risk_module",
    "risk_module_name",
    "rm_name",
    "quote",
    "events",
    "replaces",
    "replaced_by",
    "splitter1",
    "splitter2",
    "date_price_applied",
]
DATETIME_COLUMNS = ["date", "start", "expiration", "expired_on", "date_price_applied"]
NUMERICAL_COLUMNS = [
    "payout",
    "loss_prob",
    "jr_scr",
    "sr_scr",
    "pure_premium",
    "ensuro_commission",
    "partner_commission",
    "jr_coc",
    "sr_coc",
    "actual_payout",
    "premium",
    "progress",
    "duration_expected",
    "duration_actual",
]
