from mcp.server.fastmcp import FastMCP
from .tools import tools
import logging


def serve():
    logger = logging.getLogger("mcp")

    mcp = FastMCP("Reddit")

    for tool in tools:
        logger.info(f"Registering tool: {tool.__name__}")
        mcp.tool()(tool)

    logger.info("Starting MCP server...")
    mcp.run(transport="stdio")
