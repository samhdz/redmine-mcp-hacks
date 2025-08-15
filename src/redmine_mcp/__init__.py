"""
Redmine MCP Server
A Model Context Protocol server for managing Redmine issues via Claude Code
"""

try:
    from importlib.metadata import version
    __version__ = version("redmine-mcp")
except ImportError:
    # Fallback for development environments or older Python versions
    __version__ = "0.1.0"
