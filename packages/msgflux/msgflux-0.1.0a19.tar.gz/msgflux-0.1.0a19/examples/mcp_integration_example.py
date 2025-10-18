"""Example: Using MCP (Model Context Protocol) integration with msgflux.

This example demonstrates how to connect to MCP servers and use remote tools
alongside local tools in an Agent.
"""

from msgflux.nn.modules import Agent
from msgflux.models import OpenAI  # or any other model


# Example 1: MCP with stdio transport (local subprocess)
def example_stdio_mcp():
    """Example using MCP server via stdio transport."""

    # Local tool definition
    def local_calculator(operation: str, a: float, b: float) -> float:
        """Perform basic math operations."""
        if operation == "add":
            return a + b
        elif operation == "multiply":
            return a * b
        return 0

    # Create agent with MCP filesystem server
    agent = Agent(
        name="file_assistant",
        model=OpenAI("gpt-4"),
        instructions="You are a helpful assistant that can read and write files.",
        tools=[local_calculator],  # Local tools
        mcp_servers=[
            {
                "name": "fs",  # Namespace for this server's tools
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                "cwd": "/path/to/workspace",

                # Optional: Filter tools
                "include_tools": ["read_file", "write_file", "list_directory"],

                # Optional: Configure tools
                "tool_config": {
                    "read_file": {
                        "inject_vars": ["project_path"],  # Inject vars into tool params
                    },
                    "write_file": {
                        "return_direct": False  # Don't return result directly
                    }
                }
            }
        ],
        verbose=True
    )

    # Agent now has access to:
    # - local_calculator (local tool)
    # - fs__read_file (MCP tool with namespace)
    # - fs__write_file (MCP tool with namespace)
    # - fs__list_directory (MCP tool with namespace)

    response = agent("Read the file config.json and calculate the sum of values")
    print(response)


# Example 2: MCP with HTTP transport (remote server)
def example_http_mcp():
    """Example using MCP server via HTTP transport."""

    agent = Agent(
        name="weather_assistant",
        model=OpenAI("gpt-4"),
        instructions="You are a helpful assistant that can check weather.",
        mcp_servers=[
            {
                "name": "weather",
                "transport": "http",
                "base_url": "http://localhost:8080",
                "timeout": 30.0,
                "headers": {
                    "Authorization": "Bearer your-api-token"
                },

                # Optional: Exclude certain tools
                "exclude_tools": ["admin_reset", "admin_delete"],
            }
        ]
    )

    response = agent("What's the weather in São Paulo?")
    print(response)


# Example 3: Multiple MCP servers
def example_multiple_mcp():
    """Example using multiple MCP servers simultaneously."""

    agent = Agent(
        name="super_assistant",
        model=OpenAI("gpt-4"),
        instructions="You are a multi-talented assistant.",
        mcp_servers=[
            # Filesystem server
            {
                "name": "fs",
                "transport": "stdio",
                "command": "mcp-server-filesystem",
                "include_tools": ["read_file", "write_file"]
            },
            # Git server
            {
                "name": "git",
                "transport": "stdio",
                "command": "mcp-server-git",
                "exclude_tools": ["git_force_push", "git_reset_hard"]
            },
            # Remote API
            {
                "name": "api",
                "transport": "http",
                "base_url": "http://api.example.com"
            }
        ]
    )

    # Agent has tools from all servers with namespaces:
    # - fs__read_file, fs__write_file
    # - git__git_status, git__git_commit, etc.
    # - api__* (whatever the API server provides)

    response = agent(
        "Read the README.md file, check git status, and send a summary to the API"
    )
    print(response)


# Example 4: Tool config features
def example_tool_config():
    """Example demonstrating advanced tool_config features."""

    agent = Agent(
        name="configured_assistant",
        model=OpenAI("gpt-4"),
        mcp_servers=[
            {
                "name": "fs",
                "transport": "stdio",
                "command": "mcp-server-fs",
                "tool_config": {
                    # Inject specific variables
                    "read_file": {
                        "inject_vars": ["user_id", "session_id"]
                    },
                    # Return result directly without further processing
                    "get_metadata": {
                        "return_direct": True
                    },
                    # Inject all vars
                    "advanced_search": {
                        "inject_vars": True  # Injects all vars as "vars" parameter
                    }
                }
            }
        ],
        vars="context"  # Message field to extract vars from
    )

    from msgflux.message import Message

    msg = Message(
        text="Read the important file",
        context={
            "user_id": "user123",
            "session_id": "sess456"
        }
    )

    response = agent(msg)
    print(response)


if __name__ == "__main__":
    print("MCP Integration Examples")
    print("=" * 50)

    # Uncomment to run examples:
    # example_stdio_mcp()
    # example_http_mcp()
    # example_multiple_mcp()
    # example_tool_config()
