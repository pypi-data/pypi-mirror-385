"""
vMCP - Virtual Model Context Protocol
======================================

Main application entry point.
Creates and configures the FastAPI application with MCP server.
"""

import uvicorn
from vmcp.config import settings
from vmcp.utilities.logging import setup_logging, get_logger
from vmcp.proxy_server import create_app

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create the FastAPI application with MCP server
app = create_app()


def main():
    """Run the vMCP server."""
    logger.info(f"🚀 Starting vMCP server on {settings.host}:{settings.port}")

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development",
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
