class MCPError(Exception):
    """Base exception for MCP client errors."""

    pass


class MCPTimeoutError(MCPError):
    """Raised when MCP operations timeout."""

    pass


class MCPToolError(MCPError):
    """Raised when tool execution fails."""

    pass
