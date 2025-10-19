import logging
from typing import Optional

import httpx

from remnawave.controllers import (
    APITokensManagementController,
    AuthController,
    BandWidthStatsController,
    ConfigProfilesController,
    HostsBulkActionsController,
    HostsController,
    HWIDUserController,
    InboundsBulkActionsController,
    InboundsController,
    InfraBillingController,
    InternalSquadsController,
    KeygenController,
    NodesController,
    NodesUsageHistoryController,
    NodesUserUsageHistoryController,
    SubscriptionController,
    SubscriptionsController,
    SubscriptionsSettingsController,
    SubscriptionsTemplateController,
    SystemController,
    UsersBulkActionsController,
    UsersController,
    UsersStatsController,
    WebhookUtility,
    XrayConfigController,
    SubscriptionRequestHistoryController
    # WebhookUtility is not a controller, but it's included in the controllers module for convenience
)
    

class RemnawaveSDK:
    def __init__(
        self,
        client: Optional[httpx.AsyncClient] = None,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        caddy_token: Optional[str] = None,
        ssl_ignore: Optional[bool] = False,
        custom_headers: Optional[dict] = None,
    ):
        """
        Remnawave SDK init

        Args:
            client (Optional[httpx.AsyncClient]): - Default client.
            base_url (Optional[str]): - Base url of the Remnawave panel. Defaults to None.
            token (Optional[str]): - Token for authorization.
            caddy_token (Optional[str]): - Token for Caddy Auth (Headers). Defaults to None.
            ssl_ignore (Optional[bool]): - Whether to ignore SSL certificate errors. Defaults to False.
            custom_headers (Optional[dict]): - Custom headers to include in the requests. Defaults to None.
        """
        self._client = client
        self._token = token
        self.base_url = base_url
        self.caddy_token = caddy_token
        self.ssl_ignore = ssl_ignore
        self.custom_headers = custom_headers

        self._validate_params()

        if self._client is None:
            self._client = self._prepare_client()

        self.api_tokens_management = APITokensManagementController(self._client)
        self.auth = AuthController(self._client)
        self.bandwidthstats = BandWidthStatsController(self._client)
        self.config_profiles = ConfigProfilesController(self._client)
        self.hosts = HostsController(self._client)
        self.hosts_bulk_actions = HostsBulkActionsController(self._client)
        self.hwid = HWIDUserController(self._client)
        self.inbounds = InboundsController(self._client)
        self.inbounds_bulk_actions = InboundsBulkActionsController(self._client)
        self.infra_billing = InfraBillingController(self._client)
        self.internal_squads = InternalSquadsController(self._client)
        self.keygen = KeygenController(self._client)
        self.nodes = NodesController(self._client)
        self.nodes_usage_history = NodesUsageHistoryController(self._client)
        self.nodes_user_usage_history = NodesUserUsageHistoryController(self._client)
        self.subscription = SubscriptionController(self._client)
        self.subscriptions = SubscriptionsController(self._client)
        self.subscriptions_settings = SubscriptionsSettingsController(self._client)
        self.subscriptions_template = SubscriptionsTemplateController(self._client)
        self.subscription_request_history = SubscriptionRequestHistoryController(self._client)
        self.system = SystemController(self._client)
        self.users = UsersController(self._client)
        self.users_bulk_actions = UsersBulkActionsController(self._client)
        self.users_stats = UsersStatsController(self._client)
        self.webhook_utility = WebhookUtility()
        self.xray_config = XrayConfigController(self._client)

    def _validate_params(self) -> None:
        if self._client is None:
            if self.base_url is None or self._token is None:
                raise ValueError(
                    "base_url and token must be provided if client is not provided"
                )
        else:
            if self.base_url is not None or self._token is not None:
                logging.warning(
                    "base_url and token will be ignored if client is provided"
                )

    def _prepare_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._prepare_url(),
            headers=self._prepare_headers(),
            verify=not self.ssl_ignore,
        )

    def _prepare_headers(self) -> dict:
        headers = {}
        if self._token:
            headers["Authorization"] = (
                self._token
                if self._token.startswith("Bearer ")
                else f"Bearer {self._token}"
            )

        # X-Api-Key for Caddy (https://remna.st/security/caddy-with-custom-path#issuing-api-keys)
        if self.caddy_token is not None:
            headers["X-Api-Key"] = self.caddy_token

        if self.custom_headers:
            headers.update(self.custom_headers)

        return headers

    def _prepare_url(self) -> str:
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        if not self.base_url.endswith("/api"):
            self.base_url += "/api"

        return self.base_url
