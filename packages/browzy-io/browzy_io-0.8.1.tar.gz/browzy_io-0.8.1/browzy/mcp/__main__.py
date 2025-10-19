"""Entry point for running MCP server as a module.

Usage:
    python -m browzy.mcp
"""

import asyncio

from browzy.mcp.server import main

if __name__ == '__main__':
	asyncio.run(main())
