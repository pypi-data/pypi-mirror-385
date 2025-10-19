"""MCP verb wrappers for AssertLang SDK."""

from .verbs import MCP

# Singleton instance
mcp = MCP()

__all__ = ["mcp", "MCP"]