"""
Base connector classes for Agentic Fabric SDK.
"""

import abc
import logging
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from ..auth.token_cache import TokenManager
from ..exceptions import ConnectorError


class ConnectorContext(BaseModel):
    """Context object passed to connector instances."""

    tenant_id: str
    user_id: Optional[str] = None
    http: httpx.AsyncClient
    token_manager: "TokenManager"
    logger: logging.Logger
    metadata: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class BaseConnector(abc.ABC):
    """Base class for all connectors."""

    def __init__(self, ctx: ConnectorContext):
        self.ctx = ctx
        self.session = ctx.http
        self.logger = ctx.logger
        self.token_manager = ctx.token_manager

    @abc.abstractmethod
    async def invoke(self, method: str, **kwargs) -> Any:
        """Generic fallback invocation method."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the connector."""
        return {"status": "healthy", "connector": self.__class__.__name__}

    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata."""
        return {
            "name": self.__class__.__name__,
            "version": getattr(self, "__version__", "unknown"),
            "description": self.__doc__ or "No description available",
        }


class ToolConnector(BaseConnector):
    """Base class for tool connectors."""

    # Override in subclass
    TOOL_ID: str = ""

    def __init__(self, ctx: ConnectorContext):
        super().__init__(ctx)
        if not self.TOOL_ID:
            raise ConnectorError("TOOL_ID must be set in connector subclass")

    @abc.abstractmethod
    async def invoke(self, method: str, **kwargs) -> Any:
        """
        Invoke a tool method.
        
        Args:
            method: The tool method to invoke
            **kwargs: Method arguments
            
        Returns:
            The result of the tool invocation
        """
        pass

    async def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema/specification."""
        return {
            "tool_id": self.TOOL_ID,
            "methods": self._get_available_methods(),
            "auth_required": True,
            "scopes": getattr(self, "REQUIRED_SCOPES", []),
        }

    def _get_available_methods(self) -> list[str]:
        """Get list of available methods for this tool."""
        methods = []
        for attr_name in dir(self):
            if not attr_name.startswith("_") and callable(getattr(self, attr_name)):
                attr = getattr(self, attr_name)
                if hasattr(attr, "__annotations__") and not attr_name in [
                    "invoke",
                    "health_check",
                    "get_metadata",
                    "get_schema",
                ]:
                    methods.append(attr_name)
        return methods


class AgentConnector(BaseConnector):
    """Base class for agent connectors that speak A2A or MCP."""

    AGENT_ID: str = ""

    def __init__(self, ctx: ConnectorContext):
        super().__init__(ctx)
        if not self.AGENT_ID:
            raise ConnectorError("AGENT_ID must be set in connector subclass")

    @abc.abstractmethod
    async def invoke(self, input_text: str, **params) -> str:
        """
        Invoke the agent.
        
        Args:
            input_text: The input text/prompt for the agent
            **params: Additional parameters for the agent
            
        Returns:
            The agent's response
        """
        pass

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "agent_id": self.AGENT_ID,
            "supports_streaming": getattr(self, "SUPPORTS_STREAMING", False),
            "max_tokens": getattr(self, "MAX_TOKENS", None),
            "supported_models": getattr(self, "SUPPORTED_MODELS", []),
        }

    async def validate_input(self, input_text: str, **params) -> bool:
        """Validate input before processing."""
        if not input_text or not input_text.strip():
            return False
        return True


class MCPConnector(BaseConnector):
    """Base class for MCP (Model Context Protocol) connectors."""

    MCP_VERSION: str = "1.0"
    SERVER_NAME: str = ""

    def __init__(self, ctx: ConnectorContext):
        super().__init__(ctx)
        if not self.SERVER_NAME:
            raise ConnectorError("SERVER_NAME must be set in MCP connector subclass")

    @abc.abstractmethod
    async def list_tools(self) -> list[Dict[str, Any]]:
        """List available tools from the MCP server."""
        pass

    @abc.abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool on the MCP server."""
        pass

    async def invoke(self, method: str, **kwargs) -> Any:
        """Generic invoke method for MCP connectors."""
        if method == "list_tools":
            return await self.list_tools()
        elif method == "call_tool":
            return await self.call_tool(
                kwargs.get("tool_name", ""), kwargs.get("arguments", {})
            )
        else:
            raise ConnectorError(f"Unknown method: {method}")

    async def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "name": self.SERVER_NAME,
            "version": self.MCP_VERSION,
            "tools": await self.list_tools(),
        }


class HTTPConnectorMixin:
    """Mixin for connectors that make HTTP requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = kwargs.get("base_url", "")
        self.default_headers = kwargs.get("default_headers", {})

    async def _make_request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request with proper error handling."""
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        request_headers = {**self.default_headers, **(headers or {})}

        try:
            response = await self.session.request(
                method, url, headers=request_headers, **kwargs
            )
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise ConnectorError(f"HTTP request failed: {e}")

    async def _get(self, path: str, **kwargs) -> httpx.Response:
        """Make a GET request."""
        return await self._make_request("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs) -> httpx.Response:
        """Make a POST request."""
        return await self._make_request("POST", path, **kwargs)

    async def _put(self, path: str, **kwargs) -> httpx.Response:
        """Make a PUT request."""
        return await self._make_request("PUT", path, **kwargs)

    async def _delete(self, path: str, **kwargs) -> httpx.Response:
        """Make a DELETE request."""
        return await self._make_request("DELETE", path, **kwargs) 