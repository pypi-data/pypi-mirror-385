"""Custom error classes for MCP Client Credentials."""


class MCPClientCredentialsError(Exception):
    """Base error class for MCP Client Credentials errors."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


class OAuthDiscoveryError(MCPClientCredentialsError):
    """Error thrown when OAuth discovery fails."""

    def __init__(self, message: str, server_url: str, cause: Exception | None = None):
        super().__init__(f"OAuth discovery failed for {server_url}: {message}", cause)
        self.server_url = server_url


class TokenAcquisitionError(MCPClientCredentialsError):
    """Error thrown when token acquisition fails."""

    def __init__(
        self,
        message: str,
        token_endpoint: str,
        status_code: int | None = None,
        cause: Exception | None = None,
    ):
        status_msg = f" (HTTP {status_code})" if status_code else ""
        super().__init__(
            f"Failed to acquire token from {token_endpoint}{status_msg}: {message}",
            cause,
        )
        self.token_endpoint = token_endpoint
        self.status_code = status_code


class TokenValidationError(MCPClientCredentialsError):
    """Error thrown when token validation fails."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(f"Token validation failed: {message}", cause)


class ConnectionError(MCPClientCredentialsError):
    """Error thrown when connection to MCP server fails."""

    def __init__(
        self,
        message: str,
        server_name: str,
        server_url: str,
        cause: Exception | None = None,
    ):
        super().__init__(
            f'Connection failed to "{server_name}" at {server_url}: {message}', cause
        )
        self.server_name = server_name
        self.server_url = server_url


class InvalidCredentialsError(MCPClientCredentialsError):
    """Error thrown when credentials are invalid."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(f"Invalid credentials: {message}", cause)
