# langchain-mcp-m2m

LangChain MCP client with OAuth 2.0 Client Credentials (M2M) support.

## Install

```bash
pip install langchain-mcp-m2m
```

## Usage

```python
from langchain_mcp_m2m import MCPClientCredentials

client = MCPClientCredentials({
    "server": {
        "url": "http://localhost:3301/mcp",
        "transport": "streamable_http",
        "auth": {
            "client_id": "your-client-id",
            "client_secret": "your-client-secret"
        }
    }
})

await client.initialize()
tools = await client.get_tools()
```

Full documentation: https://github.com/LocusTechnologies/langchain-mcp-m2m

## License

MIT
