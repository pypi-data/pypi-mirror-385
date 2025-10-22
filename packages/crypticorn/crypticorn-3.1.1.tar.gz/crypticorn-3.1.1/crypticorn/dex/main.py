from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

from crypticorn._internal.warnings import CrypticornDeprecatedSince31
from crypticorn.dex import (
    ApiClient,
    Configuration,
    SignalsApi,
    StatusApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class DexClient(SignalsApi, StatusApi):
    """
    A client for interacting with the Crypticorn DEX API.
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
        self._signals = SignalsApi(self.base_client, is_sync=is_sync)
        self._status = StatusApi(self.base_client, is_sync=is_sync)

    @property
    @deprecated(
        "Accessing dex.signals is deprecated. Use direct method calls instead (e.g., dex.get_signals())"
    )
    def signals(self):
        warnings.warn(
            "Accessing dex.signals is deprecated. Use direct method calls instead (e.g., dex.get_signals())",
            category=CrypticornDeprecatedSince31,
        )
        return self._signals

    @property
    @deprecated(
        "Accessing dex.status is deprecated. Use direct method calls instead (e.g., dex.ping())"
    )
    def status(self):
        warnings.warn(
            "Accessing dex.status is deprecated. Use direct method calls instead (e.g., dex.ping())",
            category=CrypticornDeprecatedSince31,
        )
        return self._status
