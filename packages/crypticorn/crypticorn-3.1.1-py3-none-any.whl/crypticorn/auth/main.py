from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

from crypticorn._internal.warnings import CrypticornDeprecatedSince31
from crypticorn.auth import (
    AdminApi,
    ApiClient,
    AuthApi,
    Configuration,
    UserApi,
    WalletApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class AuthClient(AdminApi, AuthApi, UserApi, WalletApi):
    """
    A client for interacting with the Crypticorn Auth API.
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
        self._admin = AdminApi(self.base_client, is_sync=is_sync)
        self._user = UserApi(self.base_client, is_sync=is_sync)
        self._wallet = WalletApi(self.base_client, is_sync=is_sync)
        self._login = AuthApi(self.base_client, is_sync=is_sync)

    @property
    @deprecated(
        "Accessing auth.admin is deprecated. Use direct method calls instead (e.g., auth.get_users())"
    )
    def admin(self):
        warnings.warn(
            "Accessing auth.admin is deprecated. Use direct method calls instead (e.g., auth.get_users())",
            category=CrypticornDeprecatedSince31,
        )
        return self._admin

    @property
    @deprecated(
        "Accessing auth.user is deprecated. Use direct method calls instead (e.g., auth.get_user())"
    )
    def user(self):
        warnings.warn(
            "Accessing auth.user is deprecated. Use direct method calls instead (e.g., auth.get_user())",
            category=CrypticornDeprecatedSince31,
        )
        return self._user

    @property
    @deprecated(
        "Accessing auth.wallet is deprecated. Use direct method calls instead (e.g., auth.add_wallet())"
    )
    def wallet(self):
        warnings.warn(
            "Accessing auth.wallet is deprecated. Use direct method calls instead (e.g., auth.add_wallet())",
            category=CrypticornDeprecatedSince31,
        )
        return self._wallet

    @property
    @deprecated(
        "Accessing auth.login is deprecated. Use direct method calls instead (e.g., auth.authorize_user())"
    )
    def login(self):
        warnings.warn(
            "Accessing auth.login is deprecated. Use direct method calls instead (e.g., auth.authorize_user())",
            category=CrypticornDeprecatedSince31,
        )
        return self._login
