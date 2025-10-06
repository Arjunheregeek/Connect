# Connect Single Agent README

## Overview
A Single Stateful LangGraph Agent that connects to the Connect MCP server via HTTP to perform intelligent queries on professional network data.

## Architecture
- **Single Stateful Agent Pattern**: One agent with persistent state throughout execution cycles
- **Three-Node Workflow**: Planner → Tool Executor → Synthesizer
- **HTTP Communication**: Connects to existing MCP server at localhost:8000
- **State Persistence**: Maintains context across multiple tool executions
- **Modular Design**: Clean separation of concerns with organized packages

## Project Structure

```
agent/
├── __init__.py                    # Main package exports
├── README.md                      # This file
├── nodes.py                       # Workflow node implementations
├── workflow.py                    # LangGraph workflow definition
├── state.py                       # Backward compatibility facade
│
├── mcp_client/                    # MCP HTTP Client Package
│   ├── __init__.py                # Client exports
│   ├── base_client.py             # Core HTTP communication
│   ├── tool_client.py             # High-level tool interfaces (24 tools)
│   ├── mcp_client.py              # Main client facade
│   └── types.py                   # MCP client data structures
│                                  #   (MCPResponse, ToolCall, etc.)
│
└── state/                         # State Management Package
    ├── __init__.py                # State exports
    ├── enums.py                   # Status enumerations
    ├── plan.py                    # Execution plan structures
    ├── types.py                   # Agent state data structures
    └── manager.py                 #   (AgentState TypedDict, etc.)
                                   # State management utilities
```

## Key Components

### MCP Client Package (`mcp_client/`)
- **Purpose**: HTTP communication with Connect MCP server
- **Features**: 24 tool interfaces, error handling, connection pooling
- **Main Classes**: `MCPClient`, `MCPResponse`, `ToolCall`
- **Types**: MCP-specific data structures in `mcp_client/types.py`

### State Management Package (`state/`)
- **Purpose**: Agent workflow state tracking and management
- **Features**: Immutable updates, status tracking, execution plans
- **Main Classes**: `AgentState`, `WorkflowStatus`, `StateManager`
- **Types**: Agent-specific data structures in `state/types.py`

### Workflow Nodes (`nodes.py`)
- **Planner Node**: Analyzes queries and creates execution plans
- **Tool Executor Node**: Executes MCP tools based on plans
- **Synthesizer Node**: Combines results into final responses

## Implementation Progress
1. ✅ Setup project structure
2. ✅ Build MCP HTTP Client (modular package)
3. ✅ Design Agent State Management (modular package)  
4. 🔄 Implement Workflow Nodes (in progress)
5. ⏳ Create LangGraph Workflow
6. ⏳ Build Main Runner
7. ⏳ Testing and Integration

## Usage Examples

### MCP Client
```python
from agent.mcp_client import MCPClient

async with MCPClient() as client:
    # Direct tool access
    response = await client.tools.find_people_by_skill("python")
    
    # Natural language search
    response = await client.tools.natural_language_search("Who are AI experts?")
```

### State Management
```python
from agent.state import AgentState, WorkflowStatus, StateManager

# Create initial state
state = StateManager.create_initial_state("Find Python experts", "conv-123")

# Update workflow status
state = StateManager.update_status(state, WorkflowStatus.PLANNING)

# Add tool results
state = StateManager.add_tool_result(state, "step-1", "find_people_by_skill", 
                                   results, 1.2)
```

## Dependencies
- **langgraph**: Workflow orchestration
- **aiohttp**: HTTP client for MCP communication  
- **typing**: Type hints and validation
- **dataclasses**: Data structure definitions
- **datetime**: Timestamp tracking

## Notes
- Both `mcp_client/types.py` and `state/types.py` exist by design
- They serve different purposes and are in separate namespaces
- The modular structure allows for clean imports and maintainability
- Backward compatibility is maintained through facade files