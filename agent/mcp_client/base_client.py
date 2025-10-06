"""
MCP Base Client

This module provides the core HTTP communication functionality for the MCP client.
It handles JSON-RPC formatting, authentication, connection management, and error handling.
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional

from .types import MCPResponse, MCPClientConfig, MCPClientError, MCPErrorCode

logger = logging.getLogger(__name__)

class MCPBaseClient:
    """
    Base HTTP client for MCP communication.
    
    Handles:
    - JSON-RPC 2.0 request/response formatting
    - Authentication via X-API-Key header
    - Connection management and retry logic
    - Error handling with structured responses
    """
    
    def __init__(self, config: MCPClientConfig):
        """
        Initialize the base MCP client.
        
        Args:
            config: Client configuration
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_counter = 0
        
        # Connection settings
        self.connector = aiohttp.TCPConnector(
            limit=config.connection_pool_limit,
            limit_per_host=config.connection_per_host_limit,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout,
                headers={"X-API-Key": self.config.api_key}
            )
    
    async def close(self):
        """Close the HTTP session and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        if self.connector:
            await self.connector.close()
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        self._request_counter += 1
        return f"agent_req_{int(time.time())}_{self._request_counter}"
    
    async def _handle_response(
        self, 
        response: aiohttp.ClientResponse, 
        request_id: str, 
        execution_time: float
    ) -> MCPResponse:
        """Handle HTTP response and convert to MCPResponse"""
        # Handle HTTP errors
        if response.status == 401:
            raise MCPClientError(
                "Authentication failed - check X-API-Key",
                error_code=MCPErrorCode.AUTHENTICATION_ERROR.value
            )
        elif response.status == 403:
            raise MCPClientError(
                "Authorization failed - invalid API key",
                error_code=MCPErrorCode.AUTHORIZATION_ERROR.value
            )
        elif response.status >= 400:
            error_text = await response.text()
            raise MCPClientError(
                f"HTTP {response.status}: {error_text}",
                error_code=response.status
            )
        
        # Parse JSON response
        try:
            response_data = await response.json()
        except json.JSONDecodeError as e:
            raise MCPClientError(f"Invalid JSON response: {e}")
        
        # Handle JSON-RPC 2.0 errors (for POST requests)
        if "error" in response_data and response_data["error"] is not None:
            error_info = response_data["error"]
            return MCPResponse(
                success=False,
                error_code=error_info.get("code") if isinstance(error_info, dict) else None,
                error_message=error_info.get("message") if isinstance(error_info, dict) else str(error_info),
                request_id=request_id,
                execution_time=execution_time
            )
        
        # Success response
        result_data = response_data.get("result") if "result" in response_data else response_data
        return MCPResponse(
            success=True,
            data=result_data,
            request_id=request_id,
            execution_time=execution_time
        )
    
    async def make_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        endpoint: str = "/mcp",
        http_method: str = "POST"
    ) -> MCPResponse:
        """
        Make a JSON-RPC 2.0 request to the MCP server.
        
        Args:
            method: MCP method name (e.g., "tools/list", "tools/call")
            params: Method parameters
            endpoint: Server endpoint to call
            http_method: HTTP method to use (GET or POST)
            
        Returns:
            MCPResponse with structured result or error information
        """
        await self._ensure_session()
        
        request_id = self._generate_request_id()
        start_time = time.time()
        
        # Build JSON-RPC 2.0 request
        request_payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        
        if params is not None:
            request_payload["params"] = params
        
        url = f"{self.config.base_url.rstrip('/')}{endpoint}"
        
        # Retry logic for transient failures
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Making MCP request (attempt {attempt + 1}): {method}")
                
                # Choose HTTP method based on endpoint
                if http_method.upper() == "GET":
                    async with self.session.get(url) as response:
                        execution_time = time.time() - start_time
                        return await self._handle_response(response, request_id, execution_time)
                else:
                    async with self.session.post(url, json=request_payload) as response:
                        execution_time = time.time() - start_time
                        return await self._handle_response(response, request_id, execution_time)
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            
            except MCPClientError:
                # Don't retry client errors (auth, validation, etc.)
                raise
        
        # All retries exhausted
        raise MCPClientError(
            f"Request failed after {self.config.max_retries + 1} attempts: {last_exception}",
            error_code=MCPErrorCode.INTERNAL_ERROR.value
        )