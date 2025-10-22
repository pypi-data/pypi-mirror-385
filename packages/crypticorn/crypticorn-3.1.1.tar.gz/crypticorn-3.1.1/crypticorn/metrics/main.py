from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

from crypticorn._internal.warnings import CrypticornDeprecatedSince31
from crypticorn.metrics import (
    ApiClient,
    Configuration,
    IndicatorsApi,
    LogsApi,
    MarketsApi,
    QuoteCurrenciesApi,
    StatusApi,
)
from crypticorn.metrics.wrapper import ExchangesApiWrapper  # wraps ExchangesApi
from crypticorn.metrics.wrapper import MarketcapApiWrapper  # wraps MarketcapApi
from crypticorn.metrics.wrapper import TokensApiWrapper  # wraps TokensApi

if TYPE_CHECKING:
    from aiohttp import ClientSession


class MetricsClient(
    ExchangesApiWrapper,
    IndicatorsApi,
    LogsApi,
    MarketcapApiWrapper,
    MarketsApi,
    QuoteCurrenciesApi,
    StatusApi,
    TokensApiWrapper,
):
    """
    A client for interacting with the Crypticorn Metrics API.
    """

    config_class = Configuration

    def __init__(
        self,
        config: Configuration,
        http_client: Optional[ClientSession] = None,
        is_sync: bool = False,
    ):
        self.config = config
        self.base_client = ApiClient(configuration=self.config)
        if http_client is not None:
            self.base_client.rest_client.pool_manager = http_client
        # Pass sync context to REST client for proper session management
        self.base_client.rest_client.is_sync = is_sync
        super().__init__(self.base_client, is_sync=is_sync)
        # TODO: remove everything below this line in v4
        self._status = StatusApi(self.base_client, is_sync=is_sync)
        self._indicators = IndicatorsApi(self.base_client, is_sync=is_sync)
        self._logs = LogsApi(self.base_client, is_sync=is_sync)
        self._marketcap = MarketcapApiWrapper(self.base_client, is_sync=is_sync)
        self._markets = MarketsApi(self.base_client, is_sync=is_sync)
        self._tokens = TokensApiWrapper(self.base_client, is_sync=is_sync)
        self._exchanges = ExchangesApiWrapper(self.base_client, is_sync=is_sync)
        self._quote_currencies = QuoteCurrenciesApi(self.base_client, is_sync=is_sync)

    @property
    @deprecated(
        "Accessing metrics.status is deprecated. Use direct method calls instead (e.g., metrics.ping())"
    )
    def status(self):
        warnings.warn(
            "Accessing metrics.status is deprecated. Use direct method calls instead (e.g., metrics.ping())",
            category=CrypticornDeprecatedSince31,
        )
        return self._status

    @property
    @deprecated(
        "Accessing metrics.indicators is deprecated. Use direct method calls instead (e.g., metrics.get_indicators())"
    )
    def indicators(self):
        warnings.warn(
            "Accessing metrics.indicators is deprecated. Use direct method calls instead (e.g., metrics.get_indicators())",
            category=CrypticornDeprecatedSince31,
        )
        return self._indicators

    @property
    @deprecated(
        "Accessing metrics.logs is deprecated. Use direct method calls instead (e.g., metrics.get_logs())"
    )
    def logs(self):
        warnings.warn(
            "Accessing metrics.logs is deprecated. Use direct method calls instead (e.g., metrics.get_logs())",
            category=CrypticornDeprecatedSince31,
        )
        return self._logs

    @property
    @deprecated(
        "Accessing metrics.marketcap is deprecated. Use direct method calls instead (e.g., metrics.get_marketcap_symbols_fmt())"
    )
    def marketcap(self):
        warnings.warn(
            "Accessing metrics.marketcap is deprecated. Use direct method calls instead (e.g., metrics.get_marketcap_symbols_fmt())",
            category=CrypticornDeprecatedSince31,
        )
        return self._marketcap

    @property
    @deprecated(
        "Accessing metrics.markets is deprecated. Use direct method calls instead (e.g., metrics.get_markets())"
    )
    def markets(self):
        warnings.warn(
            "Accessing metrics.markets is deprecated. Use direct method calls instead (e.g., metrics.get_markets())",
            category=CrypticornDeprecatedSince31,
        )
        return self._markets

    @property
    @deprecated(
        "Accessing metrics.tokens is deprecated. Use direct method calls instead (e.g., metrics.get_stable_tokens_fmt())"
    )
    def tokens(self):
        warnings.warn(
            "Accessing metrics.tokens is deprecated. Use direct method calls instead (e.g., metrics.get_stable_tokens_fmt())",
            category=CrypticornDeprecatedSince31,
        )
        return self._tokens

    @property
    @deprecated(
        "Accessing metrics.exchanges is deprecated. Use direct method calls instead (e.g., metrics.get_available_exchanges_fmt())"
    )
    def exchanges(self):
        warnings.warn(
            "Accessing metrics.exchanges is deprecated. Use direct method calls instead (e.g., metrics.get_available_exchanges_fmt())",
            category=CrypticornDeprecatedSince31,
        )
        return self._exchanges

    @property
    @deprecated(
        "Accessing metrics.quote_currencies is deprecated. Use direct method calls instead (e.g., metrics.get_quote_currencies())"
    )
    def quote_currencies(self):
        warnings.warn(
            "Accessing metrics.quote_currencies is deprecated. Use direct method calls instead (e.g., metrics.get_quote_currencies())",
            category=CrypticornDeprecatedSince31,
        )
        return self._quote_currencies
