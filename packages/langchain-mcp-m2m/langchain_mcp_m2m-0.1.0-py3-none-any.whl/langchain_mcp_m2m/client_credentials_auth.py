"""OAuth 2.0 Client Credentials (M2M) Authentication Provider for MCP.

This module implements the Client Credentials grant type for machine-to-machine
authentication with MCP servers, compatible with the MCP SDK's auth provider interface.

**Auto-Discovery**: Just provide client_id and client_secret. Everything else is auto-discovered.
"""

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx
from mcp.client.auth import OAuthClientProvider
from mcp.shared.auth import OAuthMetadata, ProtectedResourceMetadata

from .errors import (
    InvalidCredentialsError,
    OAuthDiscoveryError,
    TokenAcquisitionError,
)


@dataclass
class ClientCredentialsConfig:
    """Configuration for Client Credentials authentication."""

    client_id: str
    """OAuth Client ID for M2M authentication"""

    client_secret: str
    """OAuth Client Secret for M2M authentication"""

    refresh_buffer: int = 60
    """How long before expiry to refresh token (seconds). Default: 60"""


@dataclass
class TokenCache:
    """Internal token cache structure."""

    access_token: str
    expires_at: float  # Unix timestamp in seconds
    token_type: str
    scope: str | None = None


class ClientCredentialsAuthProvider(OAuthClientProvider):
    """Client Credentials OAuth Provider for MCP.

    This provider implements the OAuth 2.0 Client Credentials flow for machine-to-machine
    authentication. It does NOT require user interaction and is suitable for automated
    systems and backend services.

    **Key features:**
    - Automatic token acquisition and refresh
    - Token caching with configurable expiry buffer
    - Works with any OAuth 2.0 provider (AWS Cognito, Auth0, Okta, etc.)
    - Auto-discovers token endpoint from MCP server metadata
    - Scopes are pre-allocated (no need to specify)

    Example:
        ```python
        auth_provider = ClientCredentialsAuthProvider(
            ClientCredentialsConfig(
                client_id="your-client-id",
                client_secret="your-client-secret"
            )
        )

        await auth_provider.initialize("http://localhost:3301/mcp")
        tokens = await auth_provider.tokens()
        ```
    """

    def __init__(self, config: ClientCredentialsConfig):
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.refresh_buffer = config.refresh_buffer
        self._token_cache: TokenCache | None = None
        self._resource_metadata: ProtectedResourceMetadata | None = None
        self._auth_server_metadata: OAuthMetadata | None = None
        self._is_initialized = False
        self._http_client = httpx.AsyncClient()

    async def initialize(self, server_url: str) -> None:
        """Initialize by discovering OAuth metadata from the MCP server.

        This is called automatically by the wrapper before connecting.

        Args:
            server_url: The MCP server URL
        """
        if self._is_initialized:
            return

        try:
            # Step 1: Discover protected resource metadata from MCP server
            metadata_url = urljoin(server_url, "/.well-known/oauth-protected-resource")
            try:
                response = await self._http_client.get(metadata_url)
                response.raise_for_status()
                resource_data = response.json()
            except Exception as e:
                raise OAuthDiscoveryError(
                    "Failed to fetch protected resource metadata. "
                    "Ensure the MCP server exposes /.well-known/oauth-protected-resource endpoint.",
                    server_url,
                    e,
                )

            if not resource_data.get("authorization_servers"):
                raise OAuthDiscoveryError(
                    "No authorization servers found in protected resource metadata.",
                    server_url,
                )

            # Step 2: Discover authorization server metadata
            auth_server_url = resource_data["authorization_servers"][0]

            try:
                # Try OIDC discovery first (Cognito, Google use this)
                # Note: Can't use urljoin with leading / as it strips the path
                base_url = auth_server_url.rstrip("/")
                as_metadata_url = f"{base_url}/.well-known/openid-configuration"
                response = await self._http_client.get(as_metadata_url)
                if response.status_code == 404:
                    # Fall back to OAuth 2.0 discovery
                    as_metadata_url = f"{base_url}/.well-known/oauth-authorization-server"
                    response = await self._http_client.get(as_metadata_url)
                response.raise_for_status()
                auth_server_data = response.json()
            except Exception as e:
                raise OAuthDiscoveryError(
                    "Failed to discover authorization server metadata. "
                    "Ensure the OAuth provider exposes discovery endpoint.",
                    auth_server_url,
                    e,
                )

            if not auth_server_data.get("token_endpoint"):
                raise OAuthDiscoveryError(
                    "No token_endpoint found in authorization server metadata.",
                    auth_server_url,
                )

            self._auth_server_metadata = auth_server_data

            # Step 3: Pre-fetch access token
            try:
                await self._acquire_tokens()
            except TokenAcquisitionError as e:
                if e.status_code == 401:
                    raise InvalidCredentialsError(
                        "Client credentials were rejected by the OAuth provider. "
                        "Verify your client_id and client_secret are correct.",
                        e,
                    )
                raise

            self._is_initialized = True

        except Exception:
            self._is_initialized = False
            raise

    def get_token_endpoint(self) -> str | None:
        """Get the discovered token endpoint."""
        if self._auth_server_metadata:
            return self._auth_server_metadata.get("token_endpoint")
        return None

    @property
    def redirect_url(self) -> str:
        """Redirect URL - Not used in Client Credentials flow."""
        return "urn:ietf:wg:oauth:2.0:oob"  # RFC 8252: Out-of-band

    @property
    def client_metadata(self) -> dict[str, Any]:
        """Client metadata for registration (if needed)."""
        return {
            "redirect_uris": [self.redirect_url],
            "client_name": "MCP Client Credentials Client",
            "grant_types": ["client_credentials"],
            "token_endpoint_auth_method": "client_secret_post",
        }

    def client_information(self) -> dict[str, str] | None:
        """Returns client information (pre-registered)."""
        return {"client_id": self.client_id}

    async def tokens(self) -> dict[str, Any] | None:
        """Get current tokens (with automatic refresh).

        Returns tokens with a dummy refresh_token to prevent the SDK from
        attempting Authorization Code flow.
        """
        # If we have cached tokens that are still valid, return them
        if self._token_cache and self._is_token_valid(self._token_cache):
            return {
                "access_token": self._token_cache.access_token,
                "token_type": self._token_cache.token_type,
                "scope": self._token_cache.scope,
                "refresh_token": "__client_credentials_refresh__",  # Dummy
            }

        # If not initialized, return None
        if not self._is_initialized:
            return None

        # Acquire new tokens
        tokens = await self._acquire_tokens()

        # Add dummy refresh_token
        return {
            **tokens,
            "refresh_token": "__client_credentials_refresh__",
        }

    async def save_tokens(self, tokens: dict[str, Any]) -> None:
        """Save tokens to cache."""
        expires_in = tokens.get("expires_in", 3600)
        expires_at = time.time() + expires_in

        self._token_cache = TokenCache(
            access_token=tokens["access_token"],
            expires_at=expires_at,
            token_type=tokens["token_type"],
            scope=tokens.get("scope"),
        )

    async def add_client_authentication(
        self,
        headers: dict[str, str],
        params: dict[str, str],
        url: str,
        metadata: OAuthMetadata | None = None,
    ) -> None:
        """Custom client authentication for Client Credentials flow.

        Adds client_id and client_secret to the token request.
        """
        # For Client Credentials flow, send credentials in body
        params["client_id"] = self.client_id
        params["client_secret"] = self.client_secret

        # If SDK is trying to refresh, change to client_credentials grant
        if params.get("grant_type") == "refresh_token":
            params["grant_type"] = "client_credentials"
            params.pop("refresh_token", None)
        elif "grant_type" not in params:
            params["grant_type"] = "client_credentials"

    # Methods not used in Client Credentials flow

    def state(self) -> str:
        """State parameter - Not used in Client Credentials flow."""
        return ""

    async def redirect_to_authorization(self, authorization_url: str) -> None:
        """Redirect to authorization - Not applicable for Client Credentials."""
        raise RuntimeError(
            "Client Credentials flow does not use authorization redirect. "
            "This indicates the MCP SDK is attempting Authorization Code flow instead."
        )

    async def save_code_verifier(self, code_verifier: str) -> None:
        """PKCE code verifier - Not used in Client Credentials flow."""
        pass

    def code_verifier(self) -> str:
        """PKCE code verifier - Not used in Client Credentials flow."""
        raise RuntimeError("Client Credentials flow does not use PKCE")

    async def validate_resource_url(
        self, server_url: str, resource: str | None = None
    ) -> str | None:
        """Validate resource URL."""
        if resource:
            return resource
        return server_url

    async def invalidate_credentials(
        self, scope: str = "all"
    ) -> None:
        """Invalidate credentials on auth failure."""
        if scope in ("all", "tokens"):
            self._token_cache = None

    def force_refresh(self) -> None:
        """Force token refresh (useful for testing)."""
        self._token_cache = None

    # Private helper methods

    def _is_token_valid(self, cache: TokenCache) -> bool:
        """Check if cached token is still valid."""
        now = time.time()
        buffer = self.refresh_buffer
        return cache.expires_at - buffer > now

    async def _acquire_tokens(self) -> dict[str, Any]:
        """Acquire new access token using Client Credentials flow."""
        if not self._auth_server_metadata:
            raise TokenAcquisitionError(
                "Token endpoint not discovered. Call initialize() first.", "unknown"
            )

        token_endpoint = self._auth_server_metadata["token_endpoint"]

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = await self._http_client.post(
                token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except Exception as e:
            raise TokenAcquisitionError(
                f"Network error: {str(e)}", token_endpoint, cause=e
            )

        if not response.is_success:
            error_text = response.text
            error_message = f"HTTP {response.status_code} {response.reason_phrase}"

            try:
                error_data = response.json()
                if "error" in error_data:
                    desc = error_data.get("error_description", "")
                    error_message = f"{error_data['error']}: {desc}" if desc else error_data["error"]
            except Exception:
                if error_text:
                    error_message += f": {error_text}"

            raise TokenAcquisitionError(
                error_message, token_endpoint, response.status_code
            )

        try:
            token_data = response.json()
        except Exception as e:
            raise TokenAcquisitionError(
                "Invalid JSON response from token endpoint",
                token_endpoint,
                response.status_code,
                e,
            )

        if "access_token" not in token_data:
            raise TokenAcquisitionError(
                "No access_token in response", token_endpoint, response.status_code
            )

        # Cache the tokens
        await self.save_tokens(token_data)

        return token_data

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()
