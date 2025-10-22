"""FastMCP-based server for App Store Connect MCP."""

from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from app_store_connect_mcp.core.container import Container

# Create the container and MCP server
# In production, this reads directly from environment variables
container = Container()


# Initialize FastMCP with lifespan management
@asynccontextmanager
async def lifespan(app):
    """Manage the lifecycle of the MCP server."""
    try:
        yield
    finally:
        await container.cleanup()


# Create FastMCP server instance
mcp = FastMCP(name="app-store-connect-mcp", lifespan=lifespan)

# Register all domain tools with the server
container.register_all_tools(mcp)


def run():
    """Run the FastMCP server."""
    mcp.run()


def main() -> None:
    """Main entry point for the server."""
    run()


if __name__ == "__main__":
    main()


__all__ = [
    "mcp",
    "run",
    "main",
]
