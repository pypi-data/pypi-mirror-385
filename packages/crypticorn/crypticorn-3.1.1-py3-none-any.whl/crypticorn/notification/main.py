from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

from crypticorn._internal.warnings import CrypticornDeprecatedSince31
from crypticorn.notification import (
    ApiClient,
    Configuration,
    NotificationsApi,
    SettingsApi,
    StatusApi,
    TemplatesApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class NotificationClient(NotificationsApi, SettingsApi, StatusApi, TemplatesApi):
    """
    A client for interacting with the Crypticorn Notification API.
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
        self._notifications = NotificationsApi(self.base_client, is_sync=is_sync)
        self._templates = TemplatesApi(self.base_client, is_sync=is_sync)
        self._settings = SettingsApi(self.base_client, is_sync=is_sync)
        self._status = StatusApi(self.base_client, is_sync=is_sync)

    @property
    @deprecated(
        "Accessing notification.notifications is deprecated. Use direct method calls instead (e.g., notification.create_notification())"
    )
    def notifications(self):
        warnings.warn(
            "Accessing notification.notifications is deprecated. Use direct method calls instead (e.g., notification.create_notification())",
            category=CrypticornDeprecatedSince31,
        )
        return self._notifications

    @property
    @deprecated(
        "Accessing notification.templates is deprecated. Use direct method calls instead (e.g., notification.get_templates())"
    )
    def templates(self):
        warnings.warn(
            "Accessing notification.templates is deprecated. Use direct method calls instead (e.g., notification.get_templates())",
            category=CrypticornDeprecatedSince31,
        )
        return self._templates

    @property
    @deprecated(
        "Accessing notification.settings is deprecated. Use direct method calls instead (e.g., notification.get_settings())"
    )
    def settings(self):
        warnings.warn(
            "Accessing notification.settings is deprecated. Use direct method calls instead (e.g., notification.get_settings())",
            category=CrypticornDeprecatedSince31,
        )
        return self._settings

    @property
    @deprecated(
        "Accessing notification.status is deprecated. Use direct method calls instead (e.g., notification.ping())"
    )
    def status(self):
        warnings.warn(
            "Accessing notification.status is deprecated. Use direct method calls instead (e.g., notification.ping())",
            category=CrypticornDeprecatedSince31,
        )
        return self._status
