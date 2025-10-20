"""currency converter plugin module"""

from collections.abc import Generator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime

from cmem_plugin_base.dataintegration.description import (
    Plugin,
    PluginParameter,
)
from cmem_plugin_base.dataintegration.plugins import TransformPlugin

import cmem_plugin_currencies.exceptions as e
from cmem_plugin_currencies.eurofxref import get_rates_from_api, get_rates_from_dump


@dataclass
class TransformationSummary:
    """Some values for the summary"""

    historic_rate_hit: int = 0
    historic_rate_miss_date: int = 0
    historic_rate_miss_currency: int = 0
    api_rate_hit: int = 0
    api_rate_miss_currency: int = 0
    missing_currencies: set[str] = field(default_factory=set)


def get_current_date() -> str:
    """Get current date in ISO 8601 format"""
    return datetime.now(tz=UTC).strftime("%Y-%m-%d")


@Plugin(
    label="Convert currency values",
    plugin_id="cmem_plugin_currencies-transform",
    description="Converts currencies values with current and historical exchange rates",
    documentation="""
This transform plugin allows you to convert currencies from one currency to another.
It uses the Euro foreign exchange reference rates from the
[European Central Bank](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html)
to first convert a currency value to EUR (if needed) and then to another currency.

The plugin contains a data dump which starts with data from 1999-01-04
(and ends the day before it was downloaded) see the
[change log](https://github.com/eccenca/cmem-plugin-currencies/blob/main/CHANGELOG.md)
for more details. It will use the [frankfurter.app](https://www.frankfurter.app/docs/)
API to receive rates from dates which are not part of the data dump.
This API will throw an error for future days and returns data from the last trading
day for dates where it has no data.
The API reference rates are usually updated at around 16:00 CET every working day
(so you get different rates before and after 16:00 CET in case you ask for TODAYs rates).

The plugins can work with up-to 4 inputs:

1. Input: The values which you want to convert.
1. Input: The currency code of your values. If this is not `EUR`,
    the plugin will first convert your value to `EUR`.
1. Input: The date from when you want to use the exchange rate.
1. Input: The target currency code.

For the inputs 2-4, you can define static options as well.
In addition to that, there is a debug switch which outputs more background data than
just the plain values.

Here is an example of the plugin in action:
![cmem-plugin-currencies Example](https://raw.githubusercontent.com/eccenca/cmem-plugin-currencies/main/README.png)

The
[following currency codes](https://github.com/eccenca/cmem-plugin-currencies/blob/cf2ee5332ad5243da8c70ade1ed8f4612f48ba33/cmem_plugin_currencies/eurofxref-hist.csv#L1)
can be used with the plugin.
Please be aware that not all of the rates are available for all dates
(e.g. after 2022-03-01 there is no RUB rate available anymore).
""",
    parameters=[
        PluginParameter(
            name="from_currency",
            label="1. Source Currency",
            description="The currency code you want to convert from (e.g. USD).",
            default_value="USD",
        ),
        PluginParameter(
            name="date",
            label="2. Date",
            description="Set date (e.g.YYYY-MM-DD) to convert currencies based on historic rates.",
            default_value=get_current_date(),
        ),
        PluginParameter(
            name="to_currency",
            label="3. Target Currency",
            description="Enter the currency code you want to convert to (e.g.USD).",
            default_value="EUR",
        ),
        PluginParameter(
            name="debug",
            label="Debug Output",
            advanced=True,
            description="Instead of plain values, output additional background information.",
            default_value=False,
        ),
    ],
)
class CurrenciesConverter(TransformPlugin):
    """Currency Converter Transform Plugin"""

    debug: bool
    historic_rates: dict[str, dict[str, float]]
    api_rates: dict[str, dict[str, float]]
    summary: TransformationSummary

    def __init__(
        self,
        from_currency: str = "USD",
        date: str = get_current_date(),
        to_currency: str = "EUR",
        debug: bool = False,
    ):
        self.historic_rates = get_rates_from_dump()
        self.api_rates = {}
        self.summary = TransformationSummary()
        self.date = self.date_validated(date)
        self.to_currency = to_currency.upper()
        self.from_currency = from_currency.upper()
        self.debug = debug

    @staticmethod
    def date_validated(date: str) -> str:
        """Validate a date string."""
        try:
            parsed_date = datetime.fromisoformat(date).strftime("%Y-%m-%d")
        except ValueError as error:
            raise e.InvalidDateError(error) from error
        if parsed_date < "1999-01-04":
            raise e.InvalidDateError(
                f"Historic data only available until 1999-01-04 (tried {parsed_date})."
            )
        if parsed_date > get_current_date():
            raise e.InvalidDateError(f"No future data available (tried {parsed_date}).")
        return parsed_date

    def get_rate(self, currency: str, date: str) -> float:
        """Get EUR exchange rate for a currency"""
        date = self.date_validated(date)

        # try historic rates first
        if date in self.historic_rates:
            if currency in self.historic_rates[date]:
                self.summary.historic_rate_hit += 1
                self.log.info(f"hit: historic rate for {currency} on {date}")
                return self.historic_rates[date][currency]
            # we have a date but not the currency
            self.summary.historic_rate_miss_currency += 1
            self.summary.missing_currencies.add(currency)
            self.log.info(f"miss: historic rate no {currency} on {date}")
            raise e.WrongCurrencyCodeError(currency=currency, date=date)
        # we do not have the date
        self.summary.historic_rate_miss_date += 1
        self.log.info(f"miss: historic rate no data for {date} (try API now)")

        # try api rates
        if date not in self.api_rates:
            self.api_rates[date] = get_rates_from_api(date=date)
        if currency in self.api_rates[date]:
            self.summary.api_rate_hit += 1
            self.log.info(f"hit: api rate for {currency} on {date}")
            return self.api_rates[date][currency]
        self.summary.api_rate_miss_currency += 1
        self.summary.missing_currencies.add(currency)
        self.log.info(f"miss: api rate for {currency} on {date}")
        raise e.WrongCurrencyCodeError(currency=currency, date=date)

    def transform_value(self, value: float, from_currency: str, to_currency: str, date: str) -> str:
        """Convert value from one currency to another"""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            # do not convert anything if we talk about the same currency
            value_converted = value
        else:
            # convert to base currency (EUR) except if coming from EUR already
            value_in_eur = (
                value / self.get_rate(currency=from_currency, date=date)
                if from_currency != "EUR"
                else value
            )
            # convert to target currency except if target currency is EUR
            value_converted = (
                value_in_eur * self.get_rate(currency=to_currency, date=date)
                if to_currency != "EUR"
                else value_in_eur
            )

        if self.debug:
            return f"{value_converted} - {value} {from_currency} in {to_currency} on {date}"
        return str(value_converted)

    def yield_default_from_currency(self) -> Generator[str, None, None]:
        """Provide the default FROM currency code"""
        while True:
            yield self.from_currency

    def yield_default_to_currency(self) -> Generator[str, None, None]:
        """Provide the default TO currency code"""
        while True:
            yield self.to_currency

    def yield_default_date(self) -> Generator[str, None, None]:
        """Provide the default date"""
        while True:
            yield self.date

    def transform(self, inputs: Sequence[Sequence[str]]) -> Sequence[str]:
        """Do the actual transformation of values"""
        value_input = inputs[0]
        try:
            from_currency_input = iter(inputs[1])
        except IndexError:
            from_currency_input = self.yield_default_from_currency()
        try:
            date_input = iter(inputs[2])
        except IndexError:
            date_input = self.yield_default_date()
        try:
            to_currency_input = iter(inputs[3])
        except IndexError:
            to_currency_input = self.yield_default_to_currency()

        return [
            self.transform_value(
                value=float(_),
                from_currency=next(from_currency_input),
                to_currency=next(to_currency_input),
                date=next(date_input),
            )
            for _ in value_input
        ]
