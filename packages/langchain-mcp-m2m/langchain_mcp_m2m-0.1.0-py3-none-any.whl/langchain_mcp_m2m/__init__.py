"""LangChain MCP Client with OAuth 2.0 Client Credentials (M2M) Support.

This package provides a LangChain-compatible MCP client that supports
the OAuth 2.0 Client Credentials flow for machine-to-machine authentication.
"""

from .client import MCPClientCredentials
from .client_credentials_auth import (
    ClientCredentialsAuthProvider,
    ClientCredentialsConfig,
    TokenCache,
)
from .errors import (
    ConnectionError,
    InvalidCredentialsError,
    MCPClientCredentialsError,
    OAuthDiscoveryError,
    TokenAcquisitionError,
    TokenValidationError,
)
from .httpx_auth import OAuth2BearerAuth

__version__ = "0.1.0"

__all__ = [
    "MCPClientCredentials",
    "ClientCredentialsAuthProvider",
    "ClientCredentialsConfig",
    "TokenCache",
    "OAuth2BearerAuth",
    "MCPClientCredentialsError",
    "OAuthDiscoveryError",
    "TokenAcquisitionError",
    "TokenValidationError",
    "ConnectionError",
    "InvalidCredentialsError",
]
