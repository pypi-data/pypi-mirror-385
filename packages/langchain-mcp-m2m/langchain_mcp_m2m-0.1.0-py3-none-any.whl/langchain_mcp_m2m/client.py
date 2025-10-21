"""MCP Client wrapper that extends LangChain's MultiServerMCPClient
with Client Credentials (M2M) authentication support.
"""

from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient

from .client_credentials_auth import (
    ClientCredentialsAuthProvider,
    ClientCredentialsConfig,
)
from .errors import ConnectionError, OAuthDiscoveryError, TokenAcquisitionError
from .httpx_auth import OAuth2BearerAuth


class MCPClientCredentials(MultiServerMCPClient):
    """MCP Client with Client Credentials (M2M) Authentication.

    This class extends LangChain's MultiServerMCPClient to support OAuth 2.0
    Client Credentials flow for machine-to-machine authentication.

    **Super Simple API**: Just provide the server URL and your client credentials.
    Everything else (token endpoint, scopes) is auto-discovered from the MCP server's
    OAuth metadata endpoint.

    Example:
        ```python
        from langchain_mcp_m2m import MCPClientCredentials

        client = MCPClientCredentials({
            "weather-server": {
                "url": "http://localhost:3301/mcp",
                "transport": "streamable_http",
                "auth": {
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret"
                }
            }
        })

        # Connect and load tools
        await client.initialize()
        tools = await client.get_tools()

        # Use with LangChain
        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        llm = ChatAnthropic(model="claude-sonnet-4-20250514")
        agent = create_react_agent(llm, tools)
        ```
    """

    def __init__(self, config: dict[str, Any]):
        """Create a new MCPClientCredentials instance.

        Args:
            config: Dictionary of server configurations. Each server should have:
                - url: MCP server URL
                - transport: "stdio" or "streamable_http"
                - auth: Dict with "client_id" and "client_secret"
                - (optional) command/args: For stdio transport
        """
        # Store original config
        self.config = config

        # Create auth providers and transform config
        self._auth_providers: dict[str, ClientCredentialsAuthProvider] = {}
        transformed_config = {}

        for server_name, server_config in config.items():
            if "auth" in server_config:
                # Create auth provider
                auth_config = ClientCredentialsConfig(
                    client_id=server_config["auth"]["client_id"],
                    client_secret=server_config["auth"]["client_secret"],
                    refresh_buffer=server_config["auth"].get("refresh_buffer", 60),
                )
                auth_provider = ClientCredentialsAuthProvider(auth_config)
                self._auth_providers[server_name] = auth_provider

                # Build transformed config
                # Use httpx Auth for streamable_http transport
                transformed_server_config = {
                    k: v for k, v in server_config.items() if k != "auth"
                }

                # Create httpx Auth object that will inject Bearer tokens
                httpx_auth = OAuth2BearerAuth(auth_provider)
                transformed_server_config["auth"] = httpx_auth

                transformed_config[server_name] = transformed_server_config
            else:
                # No auth, pass through as-is
                transformed_config[server_name] = server_config

        # Call parent constructor
        super().__init__(transformed_config)

    async def initialize(self) -> None:
        """Initialize connections with OAuth discovery.

        This override ensures OAuth metadata is discovered before connecting.
        """
        errors: list[Exception] = []

        # First, discover OAuth metadata for all servers
        for server_name, server_config in self.config.items():
            auth_provider = self._auth_providers.get(server_name)
            if auth_provider and "url" in server_config:
                try:
                    await auth_provider.initialize(server_config["url"])
                except Exception as e:
                    # Collect errors but continue trying other servers
                    wrapped_error = ConnectionError(
                        str(e), server_name, server_config.get("url", "unknown"), e
                    )
                    errors.append(wrapped_error)

                    # If this is a critical error type, fail fast
                    if isinstance(e, (OAuthDiscoveryError, TokenAcquisitionError)):
                        raise wrapped_error

        # If we had any errors during discovery, check if we can continue
        if errors:
            # If ALL servers failed, throw
            if len(errors) == len(self.config):
                raise ConnectionError(
                    f"Failed to initialize all {len(errors)} server(s). "
                    f"First error: {errors[0]}",
                    "all",
                    "multiple",
                    errors[0],
                )
            # Otherwise log warnings but continue
            print(
                f"Warning: {len(errors)} server(s) failed to initialize. "
                "Continuing with remaining servers."
            )

        # Then call parent's initialization (connects to servers)
        try:
            # Note: MultiServerMCPClient doesn't have an initialize() method
            # The connection happens lazily when get_tools() is called
            pass
        except Exception as e:
            raise ConnectionError(str(e), "unknown", "unknown", e)

    async def close(self) -> None:
        """Close all connections and clean up auth providers."""
        # Close auth providers
        for auth_provider in self._auth_providers.values():
            await auth_provider.close()

        # Call parent close if it exists
        if hasattr(super(), "close"):
            await super().close()

    @classmethod
    def create_single_server(
        cls, server_name: str, server_config: dict[str, Any]
    ) -> "MCPClientCredentials":
        """Static factory method for creating a client with a single server.

        Args:
            server_name: Name for the server
            server_config: Server configuration dict

        Returns:
            MCPClientCredentials instance

        Example:
            ```python
            client = MCPClientCredentials.create_single_server(
                "my-server",
                {
                    "url": "http://localhost:3301/mcp",
                    "transport": "streamable_http",
                    "auth": {
                        "client_id": "your-id",
                        "client_secret": "your-secret"
                    }
                }
            )
            ```
        """
        return cls({server_name: server_config})
