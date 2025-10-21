"""
Entry point for running the Enov8 MCP server as a module.

Usage:
    python -m enov8_mcp_server
"""

from enov8_mcp_server.server import mcp

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

