# LangGraph Integration Guide

## Connect Professional Network MCP Server Integration

This guide shows how to integrate the Connect Professional Network MCP server with your LangGraph agents.

## Server Configuration

**Base URL:** `http://localhost:8000`
**API Key:** `f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3`

## Available Tools (15 total)

### Search & Discovery
- `find_person_by_name` - Find people by name
- `natural_language_search` - Natural language queries

### Skills Analysis
- `find_people_by_skill` - Find people with specific skills
- `get_person_skills` - Get skills for a person
- `find_people_with_multiple_skills` - Complex skill matching
- `get_skill_popularity` - Popular skills analytics

### Company & Professional
- `find_people_by_company` - Find people at companies
- `find_colleagues_at_company` - Find colleagues
- `get_company_employees` - Company employee lists

### Education & Location
- `find_people_by_institution` - Find alumni/students
- `find_people_by_location` - Geographic search

### Network Analysis
- `get_person_colleagues` - Professional network
- `find_people_by_experience_level` - Experience filtering

### Profile Data
- `get_person_details` - Complete profile information

### System
- `health_check` - Server health status

## Authentication

All requests require the `X-API-Key` header:
```
X-API-Key: f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3
```

## Request Format

All tool calls use JSON-RPC 2.0 format:

```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "parameter": "value"
    }
  }
}
```

## Response Format

Successful responses:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Tool response content"
      }
    ]
  }
}
```

Error responses:
```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_id",
  "result": null,
  "error": {
    "code": -32602,
    "message": "Error description",
    "data": {
      "additional": "error context"
    }
  }
}
```

## Error Codes

- `-32602`: Invalid parameters/validation error
- `-32603`: Internal server error
- `-32601`: Tool not found
- `-32600`: Invalid request format

## Usage Examples

### Basic Skill Search
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "X-API-Key: f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3" \
     http://localhost:8000/mcp \
     -d '{
       "jsonrpc": "2.0",
       "id": "skill_search",
       "method": "tools/call",
       "params": {
         "name": "find_people_by_skill",
         "arguments": {"skill": "python"}
       }
     }'
```

### Natural Language Query
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "X-API-Key: f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3" \
     http://localhost:8000/mcp \
     -d '{
       "jsonrpc": "2.0",
       "id": "nl_search",
       "method": "tools/call",
       "params": {
         "name": "natural_language_search",
         "arguments": {"question": "Who has machine learning experience at Google?"}
       }
     }'
```

### Multiple Skills Search
```bash
curl -X POST -H "Content-Type: application/json" \
     -H "X-API-Key: f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3" \
     http://localhost:8000/mcp \
     -d '{
       "jsonrpc": "2.0",
       "id": "multi_skills",
       "method": "tools/call",
       "params": {
         "name": "find_people_with_multiple_skills",
         "arguments": {
           "skills_list": ["python", "machine learning"],
           "match_type": "all"
         }
       }
     }'
```

## Input Validation

The server includes comprehensive input validation:

### Name Validation
- Must be 2-100 characters
- Supports international characters
- Cannot be empty

### Skills Validation
- Individual skills: 1-50 characters
- Skills list: Maximum 10 skills
- Match type: "any" or "all"

### Experience Levels
Valid values: `analyst`, `associate`, `c-level`, `consultant`, `director`, `engineer`, `entry`, `intern`, `junior`, `lead`, `manager`, `mid`, `principal`, `scientist`, `senior`, `vp`

### Limits
- Skill popularity limit: 1-100 results
- Question length: 3-500 characters
- Company/Institution names: 1-100 characters

## Health Check

Monitor server status:
```bash
curl -H "X-API-Key: f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3" \
     http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database_connected": true,
  "node_count": 1992,
  "query_manager_ready": true,
  "nl_search_ready": true
}
```

## List Available Tools

Get all available tools:
```bash
curl -H "X-API-Key: f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3" \
     http://localhost:8000/tools
```