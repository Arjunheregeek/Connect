# --- mcp/README.md ---
# Connect MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for the Connect Professional Network Knowledge Graph.

## Overview

The MCP server provides a secure, standardized interface to query the Connect knowledge graph using natural language and structured queries. It implements the MCP specification for seamless integration with AI assistants and other MCP-compatible clients.

## Architecture

```
mcp/
├── server.py              # FastAPI server entry point
├── config/
│   └── settings.py        # Environment configuration
├── handlers/
│   └── mcp_handlers.py    # MCP protocol handlers
├── models/
│   └── mcp_models.py      # Pydantic models for requests/responses
├── schemas/
│   └── tool_schemas.py    # Tool definitions and validation
├── services/
│   └── bridge_service.py  # Bridge to existing Connect components
└── utils/
    ├── security.py        # Authentication and security
    └── error_handling.py  # Error handling utilities
```

## Security

The MCP server implements API key authentication:

- All requests must include the `X-API-Key` header
- The API key is loaded from the `MCP_API_KEY` environment variable
- Requests without valid API keys are rejected with 401/403 errors

## Environment Variables

Add these to your `.env` file:

```env
# MCP Server Configuration
MCP_API_KEY=your-secure-api-key-here-at-least-32-characters

# Existing variables (Neo4j, OpenAI) are reused
NEO4J_URI=your-neo4j-uri
NEO_USERNAME=your-username
NEO_PASSWORD=your-password
OPENAI_API_KEY=your-openai-api-key
```

## Available Tools

1. **find_person_by_name** - Find people by name (partial matching)
2. **find_people_by_skill** - Find people with specific skills
3. **find_people_by_company** - Find people who worked at companies
4. **find_colleagues_at_company** - Find colleagues at specific companies
5. **natural_language_search** - AI-powered natural language queries
6. **health_check** - Check system health status

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables in .env file
echo "MCP_API_KEY=$(openssl rand -hex 32)" >> .env

# Start the server
python -m mcp.server

# Or with uvicorn directly
uvicorn mcp.server:app --host 127.0.0.1 --port 8000
```

## API Endpoints

- `GET /` - Server information
- `GET /health` - Health check (no auth required)
- `POST /mcp` - Main MCP endpoint (requires API key)
- `GET /tools` - List available tools (requires API key)

## Example Usage

```bash
# List available tools
curl -H "X-API-Key: your-api-key" http://localhost:8000/tools

# MCP request to find people with Python skills
curl -X POST -H "Content-Type: application/json" -H "X-API-Key: your-api-key" \
  http://localhost:8000/mcp \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
      "name": "find_people_by_skill",
      "arguments": {"skill": "python"}
    }
  }'
```

## Integration with Existing Components

The MCP server uses a bridge service pattern to integrate with existing Connect components:

- **GraphDB**: Reuses existing database connection
- **QueryManager**: Leverages proven query functions
- **NaturalLanguageSearch**: Provides AI-powered search capabilities

This ensures zero breaking changes to existing functionality while adding MCP capabilities.