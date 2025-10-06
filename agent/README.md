# Connect Single Agent README

## Overview
A Single Stateful LangGraph Agent that connects to the Connect MCP server via HTTP to perform intelligent queries on professional network data.

## Architecture
- **Single Stateful Agent Pattern**: One agent with persistent state throughout execution cycles
- **Three-Node Workflow**: Planner → Tool Executor → Synthesizer
- **HTTP Communication**: Connects to existing MCP server at localhost:8000
- **State Persistence**: Maintains context across multiple tool executions

## File Structure
- `mcp_client.py` - HTTP client for connecting to MCP server
- `state.py` - Agent state management and data structures
- `nodes.py` - Implementation of the three workflow nodes
- `workflow.py` - LangGraph workflow definition and routing
- `run.py` - Main entry point for running the agent

## Implementation Steps
1. Setup project structure ✅
2. Build MCP HTTP Client
3. Design Agent State Management
4. Implement Workflow Nodes
5. Create LangGraph Workflow
6. Build Main Runner
7. Testing and Integration

## Dependencies
- langgraph
- httpx (for HTTP client)
- pydantic (for state models)
- typing (for type hints)