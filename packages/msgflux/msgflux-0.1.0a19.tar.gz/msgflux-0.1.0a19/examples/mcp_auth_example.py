"""Example demonstrating MCP authentication usage."""

import os
import asyncio
from msgflux.protocols.mcp import (
    MCPClient,
    BearerTokenAuth,
    APIKeyAuth,
    BasicAuth,
    OAuth2Auth,
    CustomHeaderAuth,
)


async def example_bearer_token():
    """Example 1: Bearer Token Authentication."""
    print("\n=== Bearer Token Auth Example ===")

    auth = BearerTokenAuth(token="your-jwt-token-here")

    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")


async def example_api_key():
    """Example 2: API Key Authentication."""
    print("\n=== API Key Auth Example ===")

    auth = APIKeyAuth(
        api_key="your-api-key-12345",
        header_name="X-API-Key"
    )

    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")


async def example_basic_auth():
    """Example 3: Basic Authentication."""
    print("\n=== Basic Auth Example ===")

    auth = BasicAuth(
        username=os.getenv("MCP_USERNAME", "user"),
        password=os.getenv("MCP_PASSWORD", "pass")
    )

    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")


async def example_oauth2_with_refresh():
    """Example 4: OAuth2 with Automatic Token Refresh."""
    print("\n=== OAuth2 Auth with Refresh Example ===")

    async def refresh_token_callback(refresh_token: str) -> dict:
        """Mock callback to refresh OAuth2 tokens."""
        print(f"Refreshing token using refresh_token: {refresh_token[:10]}...")

        # In real scenario, call your OAuth2 token endpoint
        # response = await http_client.post("https://auth.example.com/oauth/token", ...)

        return {
            "access_token": "new-access-token-123",
            "refresh_token": "new-refresh-token-456",
            "expires_in": 3600,
        }

    auth = OAuth2Auth(
        access_token="initial-access-token",
        refresh_token="initial-refresh-token",
        expires_in=3600,  # 1 hour
        refresh_callback=refresh_token_callback
    )

    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        # Token will be automatically refreshed when expired
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Check auth status
        auth_info = auth.get_auth_info()
        print(f"Auth type: {auth_info['type']}")
        print(f"Token expired: {auth_info['expired']}")


async def example_custom_headers():
    """Example 5: Custom Header Authentication."""
    print("\n=== Custom Headers Auth Example ===")

    import time
    import hashlib

    def generate_dynamic_headers():
        """Generate authentication headers dynamically."""
        timestamp = str(int(time.time()))
        # In real scenario, use your secret key
        signature = hashlib.sha256(
            f"{timestamp}:SECRET_KEY".encode()
        ).hexdigest()

        return {
            "X-Timestamp": timestamp,
            "X-Signature": signature,
            "X-Client-ID": "my-client-id",
        }

    auth = CustomHeaderAuth(headers_callback=generate_dynamic_headers)

    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")


async def example_integration_with_agent():
    """Example 6: Using Auth with Agent and ToolLibrary."""
    print("\n=== Integration with Agent Example ===")

    from msgflux.nn.modules.agent import Agent
    from msgflux.models import OpenAI

    # Setup different auth for different MCP servers
    analytics_auth = BearerTokenAuth(token=os.getenv("ANALYTICS_TOKEN", "token1"))
    database_auth = APIKeyAuth(api_key=os.getenv("DATABASE_KEY", "key1"))

    mcp_servers = [
        {
            "name": "analytics",
            "transport": "http",
            "base_url": "https://analytics.example.com/mcp",
            "auth": analytics_auth,
            "include_tools": ["get_metrics", "generate_report"],
        },
        {
            "name": "database",
            "transport": "http",
            "base_url": "https://db.example.com/mcp",
            "auth": database_auth,
            "include_tools": ["query", "insert", "update"],
        },
    ]

    # Create agent with authenticated MCP tools
    agent = Agent(
        name="data_agent",
        model=OpenAI(model="gpt-4"),
        mcp_servers=mcp_servers,
        system_prompt="You are a data analysis assistant with access to analytics and database tools."
    )

    # Use agent normally
    # response = agent("Show me the sales report for last month")
    # print(response)

    print("Agent configured with authenticated MCP servers!")
    print(f"Available MCP tool namespaces: analytics, database")


async def example_manual_token_refresh():
    """Example 7: Manual Token Management."""
    print("\n=== Manual Token Management Example ===")

    auth = BearerTokenAuth(
        token="initial-token",
        expires_in=3600
    )

    # Check if token is expired
    if auth.is_expired():
        # Manually update token
        new_token = "refreshed-token-123"  # Get from your auth service
        auth.update_token(new_token, expires_in=3600)
        print("Token manually refreshed")

    # Get auth information
    info = auth.get_auth_info()
    print(f"Auth info: {info}")

    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        print("Client connected with manually managed token")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("MCP Authentication Examples")
    print("=" * 60)

    # Note: These examples will fail if you don't have actual MCP servers
    # They are provided to show the API usage

    try:
        await example_bearer_token()
    except Exception as e:
        print(f"Note: Example failed (expected if no MCP server): {e}")

    try:
        await example_api_key()
    except Exception as e:
        print(f"Note: Example failed (expected if no MCP server): {e}")

    try:
        await example_basic_auth()
    except Exception as e:
        print(f"Note: Example failed (expected if no MCP server): {e}")

    try:
        await example_oauth2_with_refresh()
    except Exception as e:
        print(f"Note: Example failed (expected if no MCP server): {e}")

    try:
        await example_custom_headers()
    except Exception as e:
        print(f"Note: Example failed (expected if no MCP server): {e}")

    # This example doesn't require actual server
    await example_integration_with_agent()
    await example_manual_token_refresh()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
