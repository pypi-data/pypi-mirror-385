from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

from crypticorn._internal.warnings import CrypticornDeprecatedSince31
from crypticorn.hive.client import (
    ApiClient,
    Configuration,
    ModelsApi,
    StatusApi,
)
from crypticorn.hive.wrapper import DataApiWrapper  # wraps DataApi

if TYPE_CHECKING:
    from aiohttp import ClientSession


class HiveClient(DataApiWrapper, ModelsApi, StatusApi):
    """
    A client for interacting with the Crypticorn Hive API.
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
        self._models = ModelsApi(self.base_client, is_sync=is_sync)
        self._data = DataApiWrapper(self.base_client, is_sync=is_sync)
        self._status = StatusApi(self.base_client, is_sync=is_sync)

    @property
    @deprecated(
        "Accessing hive.models is deprecated. Use direct method calls on hive instead (e.g., hive.create_model())"
    )
    def models(self):
        warnings.warn(
            "Accessing hive.models is deprecated. Use direct method calls on hive instead (e.g., hive.create_model())",
            category=CrypticornDeprecatedSince31,
        )
        return self._models

    @property
    @deprecated(
        "Accessing hive.data is deprecated. Use direct method calls on hive instead (e.g., hive.download_data())"
    )
    def data(self):
        warnings.warn(
            "Accessing hive.data is deprecated. Use direct method calls on hive instead (e.g., hive.download_data())",
            category=CrypticornDeprecatedSince31,
        )
        return self._data

    @property
    @deprecated(
        "Accessing hive.status is deprecated. Use direct method calls on hive instead (e.g., hive.ping())"
    )
    def status(self):
        warnings.warn(
            "Accessing hive.status is deprecated. Use direct method calls on hive instead (e.g., hive.ping())",
            category=CrypticornDeprecatedSince31,
        )
        return self._status
