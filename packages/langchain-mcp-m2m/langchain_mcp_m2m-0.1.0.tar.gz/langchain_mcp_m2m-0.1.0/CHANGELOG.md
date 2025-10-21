# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of `langchain-mcp-m2m` Python package
- OAuth 2.0 Client Credentials (M2M) flow support for MCP clients
- Auto-discovery of OAuth metadata from MCP servers
- Automatic token acquisition and refresh
- Full LangChain `MultiServerMCPClient` compatibility
- Support for multiple MCP servers with different credentials
- Full type hints and mypy support
- Custom error classes for better error handling
- httpx Auth integration for Bearer token injection
- Support for AWS Cognito, Auth0, Okta, and other OAuth 2.0 providers
- Comprehensive documentation and examples

### Features
- `MCPClientCredentials` - Main client class extending LangChain's MultiServerMCPClient
- `ClientCredentialsAuthProvider` - OAuth provider for Client Credentials flow
- `OAuth2BearerAuth` - httpx Auth adapter for automatic token injection
- Automatic OAuth discovery from `/.well-known/oauth-protected-resource`
- Token caching with configurable refresh buffer
- Multi-server support with independent authentication
- Static factory method `create_single_server()` for simple use cases

### Dependencies
- `httpx` >=0.27.0
- `langchain-mcp-adapters` >=0.1.0
- `mcp` >=1.0.0

[0.1.0]: https://github.com/LocusTechnologies/langchain-mcp-m2m/releases/tag/v0.1.0
