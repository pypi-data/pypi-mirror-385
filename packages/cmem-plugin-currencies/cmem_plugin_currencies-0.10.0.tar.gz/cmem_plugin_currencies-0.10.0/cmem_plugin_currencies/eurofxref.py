"""Euro foreign exchange reference rates from the European Central Bank.

https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
"""

import contextlib
import csv
from http.client import NOT_FOUND
from pathlib import Path

import requests

import cmem_plugin_currencies.exceptions as e

BASE_URL = "https://api.frankfurter.app/"
MESSAGE_WRONG_DATE = "Date is not valid. Please use this format: YYYY-MM-DD"
MESSAGE_NO_DATA_FOR_DATE = "No data available for this date."


def get_rates_from_dump() -> dict[str, dict[str, float]]:
    """Get historic EUR rates.

    Returns a dict of dicts of floats.
    First level keys are dates, second level keys are currencies.
    Values are floats.

    assert get_historic_rates()["2024-07-12"]["USD"] == 1.089
    """
    rates = {}
    csv_file = Path(__file__).parent / "eurofxref-hist.csv"
    with csv_file.open() as f:
        reader = csv.reader(f)
        headers = next(reader)
        headers.pop(0)  # remove the first column (date)
        for row in reader:
            date = row.pop(0)
            _rates = {}
            for currency, rate in zip(headers, row, strict=True):
                with contextlib.suppress(ValueError):
                    _rates[currency] = float(rate)
            rates[date] = _rates
    return rates


def get_rates_from_api(date: str) -> dict[str, float]:
    """Get EUR rates from the API for a given date.

    assert get_rate_from_api(date="2024-07-12")["USD"] == 1.089
    """
    request = requests.get(BASE_URL + date, timeout=3)
    if request.status_code == NOT_FOUND:
        raise e.InvalidDateError(MESSAGE_NO_DATA_FOR_DATE)
    return dict(request.json()["rates"])
