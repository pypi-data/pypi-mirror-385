"""Advanced MCP Features: Telemetry, Auto-Reconnect, and Connection Pooling.

This example demonstrates the advanced features added to the MCP integration:
- Telemetry and observability with OpenTelemetry
- Automatic reconnection with exponential backoff
- HTTP connection pooling for improved performance
"""

from msgflux.nn.modules import Agent
from msgflux.models import OpenAI


# Example 1: Auto-reconnect with custom retry settings
def example_auto_reconnect():
    """Example showing automatic reconnection with custom settings."""

    agent = Agent(
        name="resilient_assistant",
        model=OpenAI("gpt-4"),
        mcp_servers=[
            {
                "name": "fs",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"],

                # Reconnection settings
                "max_retries": 5,  # Try up to 5 times
                "retry_delay": 2.0,  # Start with 2s delay (exponential backoff)
                "auto_reconnect": True,  # Automatically reconnect on failures
            }
        ]
    )

    # If the MCP server fails, the client will automatically:
    # 1. Wait 2 seconds and retry
    # 2. Wait 4 seconds and retry
    # 3. Wait 8 seconds and retry
    # 4. Wait 16 seconds and retry
    # 5. Wait 32 seconds and retry
    # 6. Raise MCPConnectionError if all attempts fail

    response = agent("Read the config file")
    print(response)


# Example 2: HTTP connection pooling
def example_connection_pooling():
    """Example showing HTTP connection pooling for performance."""

    agent = Agent(
        name="high_performance_assistant",
        model=OpenAI("gpt-4"),
        mcp_servers=[
            {
                "name": "api",
                "transport": "http",
                "base_url": "http://localhost:8080",

                # Connection pooling settings
                "pool_limits": {
                    "max_connections": 200,  # Maximum total connections
                    "max_keepalive_connections": 50  # Keepalive connections
                },

                # Reconnection settings
                "max_retries": 3,
                "retry_delay": 1.0,
                "auto_reconnect": True
            }
        ]
    )

    # The HTTP transport will:
    # - Reuse connections for better performance
    # - Maintain up to 50 keepalive connections
    # - Support up to 200 total concurrent connections
    # - Automatically handle connection pooling

    response = agent("Call the API multiple times")
    print(response)


# Example 3: Telemetry and observability
def example_telemetry():
    """Example showing telemetry integration.

    To enable telemetry, set environment variables:
    - MSGFLUX_TELEMETRY_REQUIRES_TRACE=true
    - MSGFLUX_TELEMETRY_SPAN_EXPORTER_TYPE=console (or otlp)
    - MSGFLUX_TELEMETRY_OTLP_ENDPOINT=http://localhost:4318/v1/traces (if using otlp)
    """

    import os

    # Enable telemetry
    os.environ["MSGFLUX_TELEMETRY_REQUIRES_TRACE"] = "true"
    os.environ["MSGFLUX_TELEMETRY_SPAN_EXPORTER_TYPE"] = "console"

    agent = Agent(
        name="instrumented_assistant",
        model=OpenAI("gpt-4"),
        mcp_servers=[
            {
                "name": "fs",
                "transport": "stdio",
                "command": "mcp-server-fs"
            }
        ]
    )

    # The following operations will create telemetry spans:
    # - mcp.client.connect: Connection to MCP server
    # - mcp.client.list_tools: Tool discovery
    # - mcp.client.call_tool: Tool execution
    # - Includes attributes like:
    #   * mcp.operation: Operation type
    #   * mcp.tool.name: Tool name (for call_tool)
    #   * mcp.duration_ms: Operation duration
    #   * mcp.connection_attempts: Retry attempts
    #   * mcp.error: Error message (if failed)

    response = agent("Read the README file")
    print(response)

    # Telemetry data will be exported to console or OTLP endpoint
    # You can use tools like Jaeger or Zipkin to visualize traces


# Example 4: Complete production setup
def example_production_setup():
    """Example showing production-ready MCP configuration."""

    agent = Agent(
        name="production_assistant",
        model=OpenAI("gpt-4"),
        instructions="You are a production-ready assistant with robust MCP integration.",
        mcp_servers=[
            # Local filesystem server with retry logic
            {
                "name": "fs",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                "cwd": "/app/workspace",

                # Resilience
                "max_retries": 5,
                "retry_delay": 1.0,
                "auto_reconnect": True,

                # Filter tools
                "include_tools": ["read_file", "write_file", "list_directory"],

                # Tool configuration
                "tool_config": {
                    "read_file": {"inject_vars": ["user_context"]},
                    "write_file": {"return_direct": False}
                }
            },

            # Remote API server with connection pooling
            {
                "name": "api",
                "transport": "http",
                "base_url": "https://api.example.com",
                "headers": {"Authorization": "Bearer ${API_TOKEN}"},

                # Performance
                "pool_limits": {
                    "max_connections": 100,
                    "max_keepalive_connections": 20
                },

                # Resilience
                "max_retries": 3,
                "retry_delay": 2.0,
                "auto_reconnect": True,

                # Timeout
                "timeout": 30.0
            }
        ],
        verbose=True
    )

    response = agent("Perform multiple operations across servers")
    print(response)


# Example 5: Monitoring connection health
def example_connection_health():
    """Example showing how to monitor MCP connection health."""

    from msgflux.protocols.mcp import MCPClient

    # Create client with custom settings
    client = MCPClient.from_http(
        base_url="http://localhost:8080",
        max_retries=3,
        retry_delay=1.0,
        auto_reconnect=True,
        pool_limits={
            "max_connections": 50,
            "max_keepalive_connections": 10
        }
    )

    async def monitor_health():
        """Monitor MCP client health."""
        try:
            async with client:
                # Check connection
                is_alive = await client.ping()
                print(f"Server alive: {is_alive}")

                # Check connection attempts
                print(f"Connection attempts: {client._connection_attempts}")

                # Check last error
                if client._last_error:
                    print(f"Last error: {client._last_error}")

                # List tools (with telemetry)
                tools = await client.list_tools()
                print(f"Available tools: {len(tools)}")

        except Exception as e:
            print(f"Health check failed: {e}")

    # Run health check
    import asyncio
    asyncio.run(monitor_health())


if __name__ == "__main__":
    print("MCP Advanced Features Examples")
    print("=" * 60)
    print()

    print("1. Auto-Reconnect")
    print("   - Exponential backoff retry logic")
    print("   - Configurable retry attempts and delays")
    print()

    print("2. Connection Pooling (HTTP)")
    print("   - Reuses connections for better performance")
    print("   - Configurable pool sizes")
    print()

    print("3. Telemetry & Observability")
    print("   - OpenTelemetry instrumentation")
    print("   - Tracks connections, tool calls, errors")
    print("   - Exports to console or OTLP (Jaeger, Zipkin)")
    print()

    print("4. Production Ready")
    print("   - Combines all features")
    print("   - Robust error handling")
    print("   - Performance optimized")
    print()

    # Uncomment to run examples:
    # example_auto_reconnect()
    # example_connection_pooling()
    # example_telemetry()
    # example_production_setup()
    # example_connection_health()
