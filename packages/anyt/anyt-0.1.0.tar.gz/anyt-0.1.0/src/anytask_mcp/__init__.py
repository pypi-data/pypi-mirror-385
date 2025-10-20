"""MCP server for AnyTask integration with Claude Code.

This module provides MCP (Model Context Protocol) server functionality
for integrating AnyTask with Claude Code.

Note: The module is named 'anytask_mcp' to avoid conflicts with the
      installed 'mcp' package.
"""

from mcp.server.fastmcp import __version__

__all__ = ["__version__"]
