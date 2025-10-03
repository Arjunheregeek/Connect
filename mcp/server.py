# --- mcp/server.py ---
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from mcp.config.settings import settings
from mcp.utils.security import verify_api_key, SecurityManager
from mcp.services.bridge_service import bridge_service
from mcp.handlers.mcp_handlers import mcp_handler
from mcp.models.mcp_models import MCPRequest, MCPResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Connect MCP Server...")
    
    try:
        # Validate security settings
        SecurityManager.validate_settings()
        
        # Initialize bridge service
        await bridge_service.initialize()
        
        logger.info("Connect MCP Server started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Connect MCP Server...")
        await bridge_service.cleanup()
        logger.info("Connect MCP Server shut down complete")

# Create FastAPI app
app = FastAPI(
    title=settings.server_name,
    version=settings.server_version,
    description="MCP Server for Connect Professional Network Knowledge Graph",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your security requirements
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Custom exception handler for HTTPExceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for HTTP exceptions to return MCP-compatible errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
        headers=SecurityManager.get_security_headers()
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "server": settings.server_name,
        "version": settings.server_version,
        "status": "running",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        }
    }

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = await bridge_service.health_check()
        return JSONResponse(
            content=health_status,
            headers=SecurityManager.get_security_headers()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)},
            headers=SecurityManager.get_security_headers()
        )

# Main MCP endpoint (requires API key)
@app.post("/mcp")
async def mcp_endpoint(
    request: MCPRequest,
    api_key: str = Depends(verify_api_key)
) -> MCPResponse:
    """
    Main MCP endpoint that handles all MCP protocol requests.
    Requires X-API-Key header for authentication.
    """
    try:
        logger.info(f"Processing MCP request: {request.method}")
        
        # Handle the MCP request
        response = await mcp_handler.handle_request(request)
        
        logger.info(f"MCP request processed successfully: {request.method}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": str(e),
                "type": "server_error"
            }
        )

# Tools list endpoint (requires API key)
@app.get("/tools")
async def list_tools(api_key: str = Depends(verify_api_key)):
    """
    Endpoint to list available tools.
    Requires X-API-Key header for authentication.
    """
    try:
        from mcp.schemas.tool_schemas import MCP_TOOLS
        return JSONResponse(
            content={"tools": MCP_TOOLS},
            headers=SecurityManager.get_security_headers()
        )
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list tools",
                "message": str(e),
                "type": "server_error"
            }
        )

# Development endpoint for testing (only in debug mode)
if settings.debug:
    @app.get("/debug/info")
    async def debug_info(api_key: str = Depends(verify_api_key)):
        """Debug endpoint - only available in debug mode"""
        return {
            "settings": {
                "host": settings.host,
                "port": settings.port,
                "debug": settings.debug,
                "server_name": settings.server_name,
                "server_version": settings.server_version
            },
            "bridge_service_initialized": bridge_service._initialized,
            "available_tools": len(mcp_handler.tool_handlers)
        }

if __name__ == "__main__":
    import uvicorn
    
    # Validate settings before starting
    try:
        settings.validate_required_settings()
        SecurityManager.validate_settings()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "mcp.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )