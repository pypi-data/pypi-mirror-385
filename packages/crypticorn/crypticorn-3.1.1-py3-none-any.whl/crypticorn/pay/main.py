from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

from crypticorn._internal.warnings import CrypticornDeprecatedSince31
from crypticorn.pay import (
    AccessApi,
    ApiClient,
    Configuration,
    CouponsApi,
    InvoicesApi,
    NOWPaymentsApi,
    PaymentsApi,
    ProductsApi,
    StatusApi,
    StripeApi,
    TokenApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class PayClient(
    AccessApi,
    CouponsApi,
    InvoicesApi,
    NOWPaymentsApi,
    PaymentsApi,
    ProductsApi,
    StatusApi,
    StripeApi,
    TokenApi,
):
    """
    A client for interacting with the Crypticorn Pay API.
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
        self._now = NOWPaymentsApi(self.base_client, is_sync=is_sync)
        self._status = StatusApi(self.base_client, is_sync=is_sync)
        self._payments = PaymentsApi(self.base_client, is_sync=is_sync)
        self._products = ProductsApi(self.base_client, is_sync=is_sync)
        self._coupons = CouponsApi(self.base_client, is_sync=is_sync)
        self._token = TokenApi(self.base_client, is_sync=is_sync)
        self._invoices = InvoicesApi(self.base_client, is_sync=is_sync)
        self._stripe = StripeApi(self.base_client, is_sync=is_sync)
        self._access = AccessApi(self.base_client, is_sync=is_sync)

    @property
    @deprecated(
        "Accessing pay.now is deprecated. Use direct method calls on pay instead (e.g., pay.create_now_payment())"
    )
    def now(self):
        warnings.warn(
            "Accessing pay.now is deprecated. Use direct method calls on pay instead (e.g., pay.create_now_payment())",
            category=CrypticornDeprecatedSince31,
        )
        return self._now

    @property
    @deprecated(
        "Accessing pay.status is deprecated. Use direct method calls on pay instead (e.g., pay.ping())"
    )
    def status(self):
        warnings.warn(
            "Accessing pay.status is deprecated. Use direct method calls on pay instead (e.g., pay.ping())",
            category=CrypticornDeprecatedSince31,
        )
        return self._status

    @property
    @deprecated(
        "Accessing pay.payments is deprecated. Use direct method calls on pay instead (e.g., pay.get_payments())"
    )
    def payments(self):
        warnings.warn(
            "Accessing pay.payments is deprecated. Use direct method calls on pay instead (e.g., pay.get_payments())",
            category=CrypticornDeprecatedSince31,
        )
        return self._payments

    @property
    @deprecated(
        "Accessing pay.products is deprecated. Use direct method calls on pay instead (e.g., pay.get_products())"
    )
    def products(self):
        warnings.warn(
            "Accessing pay.products is deprecated. Use direct method calls on pay instead (e.g., pay.get_products())",
            category=CrypticornDeprecatedSince31,
        )
        return self._products

    @property
    @deprecated(
        "Accessing pay.coupons is deprecated. Use direct method calls on pay instead (e.g., pay.get_coupons())"
    )
    def coupons(self):
        warnings.warn(
            "Accessing pay.coupons is deprecated. Use direct method calls on pay instead (e.g., pay.get_coupons())",
            category=CrypticornDeprecatedSince31,
        )
        return self._coupons

    @property
    @deprecated(
        "Accessing pay.token is deprecated. Use direct method calls on pay instead (e.g., pay.get_token())"
    )
    def token(self):
        warnings.warn(
            "Accessing pay.token is deprecated. Use direct method calls on pay instead (e.g., pay.get_token())",
            category=CrypticornDeprecatedSince31,
        )
        return self._token

    @property
    @deprecated(
        "Accessing pay.invoices is deprecated. Use direct method calls on pay instead (e.g., pay.get_invoices())"
    )
    def invoices(self):
        warnings.warn(
            "Accessing pay.invoices is deprecated. Use direct method calls on pay instead (e.g., pay.get_invoices())",
            category=CrypticornDeprecatedSince31,
        )
        return self._invoices

    @property
    @deprecated(
        "Accessing pay.stripe is deprecated. Use direct method calls on pay instead (e.g., pay.create_stripe_session())"
    )
    def stripe(self):
        warnings.warn(
            "Accessing pay.stripe is deprecated. Use direct method calls on pay instead (e.g., pay.create_stripe_session())",
            category=CrypticornDeprecatedSince31,
        )
        return self._stripe

    @property
    @deprecated(
        "Accessing pay.access is deprecated. Use direct method calls on pay instead (e.g., pay.get_access_scopes())"
    )
    def access(self):
        warnings.warn(
            "Accessing pay.access is deprecated. Use direct method calls on pay instead (e.g., pay.get_access_scopes())",
            category=CrypticornDeprecatedSince31,
        )
        return self._access
