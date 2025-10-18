"""
XMind MCP Package

智能思维导图操作和转换的MCP服务器包。
"""

from .xmind_mcp_stdio import StdioRPC, main

__version__ = "1.0.1"
__all__ = ["StdioRPC", "main"]