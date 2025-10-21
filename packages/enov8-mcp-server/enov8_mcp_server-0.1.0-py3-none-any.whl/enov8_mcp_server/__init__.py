"""
Enov8 MCP Server

A Model Context Protocol (MCP) server for interacting with Enov8 ecosystem management platform.

Provides access to:
- Systems and infrastructure
- Projects and initiatives
- Service requests and tickets
- Environment events
- Bookings and reservations
- Environments
- System instances
- System components
- Releases
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from enov8_mcp_server.server import mcp

__all__ = ["mcp", "__version__"]

