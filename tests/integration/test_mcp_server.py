"""Integration test for MCP server initialization."""

import pytest

from src.mcp_server.server import SmartTradeMCPServer


class TestMCPServer:
    """Test suite for MCP server."""

    def test_server_initialization(self):
        """Test that server initializes without errors."""
        server = SmartTradeMCPServer()
        
        assert server is not None
        assert server.server is not None
        assert server.server.name == "smart-trade-mcp"

    def test_server_has_handlers(self):
        """Test that server has required handlers registered."""
        server = SmartTradeMCPServer()
        
        # Verify handlers are registered (they're decorated methods)
        assert hasattr(server.server, 'list_tools')
        assert hasattr(server.server, 'call_tool')
        assert hasattr(server.server, 'list_resources')
        assert hasattr(server.server, 'read_resource')
