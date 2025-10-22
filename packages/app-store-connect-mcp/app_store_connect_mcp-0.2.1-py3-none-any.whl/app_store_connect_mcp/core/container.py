"""Dependency injection container for the MCP server."""

from typing import TYPE_CHECKING

from app_store_connect_mcp.clients.app_store_connect import AppStoreConnectAPI
from app_store_connect_mcp.core.protocols import APIClient, DomainHandler
from app_store_connect_mcp.domains.analytics import AnalyticsHandler
from app_store_connect_mcp.domains.app import AppHandler
from app_store_connect_mcp.domains.testflight import TestFlightHandler
from app_store_connect_mcp.domains.users import UsersHandler
from app_store_connect_mcp.domains.xcode_cloud import XcodeCloudHandler

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


class Container:
    """Dependency injection container."""

    def __init__(self, config: dict[str, str | None] | None = None):
        """Initialize container.

        Args:
            config: Optional configuration dictionary. If provided, will be passed
                   to the API client. Otherwise, API client reads from environment.
        """
        self._api_client: APIClient | None = None
        self._domain_handlers: list[DomainHandler] | None = None
        self._config = config

    def get_api_client(self) -> APIClient:
        """Get or create the API client singleton."""
        if self._api_client is None:
            self._api_client = AppStoreConnectAPI(config=self._config)
        return self._api_client

    def get_domain_handlers(self) -> list[DomainHandler]:
        """Get all domain handlers with injected dependencies."""
        if self._domain_handlers is None:
            api = self.get_api_client()
            self._domain_handlers = [
                AnalyticsHandler(api),
                AppHandler(api),
                TestFlightHandler(api),
                UsersHandler(api),
                XcodeCloudHandler(api),
            ]
        return self._domain_handlers

    def register_all_tools(self, mcp: "FastMCP") -> None:
        """Register all domain tools with the FastMCP server.

        This method iterates through all domain handlers and calls their
        register_tools method to register their tools with the MCP server.

        Args:
            mcp: The FastMCP server instance to register tools with
        """
        for handler in self.get_domain_handlers():
            handler.register_tools(mcp)

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._api_client:
            await self._api_client.aclose()
