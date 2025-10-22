import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def mcp_lifespan(app):
    """Create, manage, and delegate FastMCP server lifecycle."""

    if app.mcp_server is not None:
        logger.debug("Entering MCP lifespan...")
        async with app.mcp_app.lifespan(app):
            yield
            logger.debug("Leaving MCP lifespan...")
    else:
        logger.debug("No MCP server registered...")
        yield
