"""REST client handling, including NeonStream base class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from singer_sdk import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class NeonStream(RESTStream[str]):
    """Neon Serverless Postgres stream class."""

    url_base = "https://console.neon.tech/api/v2"
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @property
    @override
    def authenticator(self) -> BearerTokenAuthenticator:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        return BearerTokenAuthenticator(token=self.config["api_key"])

    @property
    @override
    def http_headers(self) -> dict[str, str]:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "User-Agent": f"{self.tap_name}/{self._tap.plugin_version}",
            "Content-Type": "application/json",
        }

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        params: dict[str, Any] = {}

        if self.next_page_token_jsonpath:
            params["limit"] = 100
            if next_page_token:
                params["cursor"] = next_page_token
        return params
