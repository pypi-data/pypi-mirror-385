"""httpx Auth adapter for OAuth token injection."""

from typing import AsyncGenerator

import httpx

from .client_credentials_auth import ClientCredentialsAuthProvider


class OAuth2BearerAuth(httpx.Auth):
    """httpx Auth class that injects OAuth 2.0 Bearer tokens.

    This class works with our ClientCredentialsAuthProvider to automatically
    add Bearer tokens to all HTTP requests.
    """

    def __init__(self, auth_provider: ClientCredentialsAuthProvider):
        self.auth_provider = auth_provider

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """Add Bearer token to the request."""
        # Get current token (will refresh if needed)
        tokens = await self.auth_provider.tokens()

        if tokens and tokens.get("access_token"):
            # Add Authorization header with Bearer token
            request.headers["Authorization"] = f"Bearer {tokens['access_token']}"

        # Yield the request to send it
        yield request
