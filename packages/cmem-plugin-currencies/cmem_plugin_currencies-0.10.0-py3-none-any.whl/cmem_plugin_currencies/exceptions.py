"""Plugin exceptions."""


class WrongCurrencyCodeError(Exception):
    """Wrong Currency Code Error

    will be raised when the currency code is not available in the rates.
    """

    def __init__(self, currency: str, date: str) -> None:
        self.currency = currency
        self.date = date

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        return f"No rate for {self.currency} ({self.date}) available."


class InvalidDateError(ValueError):
    """Invalid Date Error

    will be raised when the date is invalid or no data is available.
    """
