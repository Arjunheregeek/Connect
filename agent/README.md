# Connect Simplified Agent README

## Overview
A Simplified LangGraph Agent that connects to the Connect MCP server via HTTP to perform intelligent queries on professional network data containing 1,992+ professional profiles.

## Architecture
- **Simplified Linear Workflow**: Planner → Executor → Synthesizer (no cycles)
- **Real MCP Integration**: Direct HTTP communication to MCP server with 24+ tools
- **Minimal State Management**: Simple AgentState TypedDict for tracking execution
- **Working Implementation**: Proven to return real data from Neo4j knowledge graph

## Project Structure

```
agent/
├── __init__.py                    # Main package exports
├── README.md                      # This file
├── details.md                     # Additional documentation
│
├── mcp_client/                    # MCP HTTP Client Package
│   ├── __init__.py                # Client exports
│   ├── base_client.py             # Core HTTP communication
│   ├── tool_client.py             # High-level tool interfaces (24 tools)
│   ├── mcp_client.py              # Main client facade
│   └── types.py                   # MCP client data structures
│
├── nodes/                         # Simplified Node Implementations
│   ├── __init__.py                # Node exports
│   ├── planner/
│   │   ├── __init__.py
│   │   └── simple_planner.py      # Basic planning without complexity
│   ├── executor/
│   │   ├── __init__.py
│   │   └── simple_executor.py     # Real MCP tool execution
│   └── synthesizer/
│       ├── __init__.py
│       └── simple_synthesizer.py  # Response formatting
│
├── state/                         # Minimal State Management
│   ├── __init__.py                # State exports
│   └── types.py                   # AgentState TypedDict only
│
└── workflow/                      # LangGraph Workflow
    ├── __init__.py                # Workflow exports
    └── graph_builder.py           # Linear workflow builder
```

## Key Components

### MCP Client Package (`mcp_client/`)
- **Purpose**: HTTP communication with Connect MCP server
- **Features**: 24+ tool interfaces, error handling, connection management
- **Main Classes**: `MCPClient`, `MCPResponse`, `ToolCall`
- **Data**: Access to 1,992+ professional profiles in Neo4j knowledge graph

### Simplified Nodes (`nodes/`)
- **Simple Planner**: Basic query analysis and tool selection
- **Simple Executor**: Direct MCP tool execution with real data retrieval
- **Simple Synthesizer**: Response formatting and data presentation

### Workflow (`workflow/`)
- **Graph Builder**: Creates linear LangGraph workflow without cycles
- **No Complexity**: Removed retry logic, quality assessment, and checkpointers

### State Management (`state/`)
- **Minimal State**: Simple `AgentState` TypedDict for tracking
- **No Complex Management**: Removed state manager and status enums

## Implementation Status
1. ✅ MCP Client Package (fully working)
2. ✅ Simplified Node Implementations (working with real data)
3. ✅ Linear LangGraph Workflow (no cyclical complexity)
4. ✅ Working Demo Integration (chatbot functionality)
5. ✅ Agent Folder Cleanup (removed complex/unused files)
6. 🔄 Complete agent_run.py (in progress)

## Usage Examples

### Working Chatbot (working_demo.py)
```python
from agent.workflow.graph_builder import WorkflowGraphBuilder

# Create simplified agent
workflow_builder = WorkflowGraphBuilder()
workflow = await workflow_builder.build_workflow()

# Interactive chatbot
while True:
    query = input("\nAsk me about our professional network: ")
    if query.lower() in ['quit', 'exit']:
        break
    
    response = await workflow.ainvoke({"query": query, "session_id": "demo"})
    print(f"\n{response['final_response']}")
```

### Direct MCP Client Usage
```python
from agent.mcp_client import MCPClient

async with MCPClient() as client:
    # Find Python developers (returns real data)
    response = await client.tools.find_people_by_skill("python")
    
    # Natural language search on knowledge graph
    response = await client.tools.natural_language_search("Who are AI experts?")
```

### Real Results Examples
- **Python Developers**: 22 professionals found
- **Google Employees**: 6 professionals found  
- **IIT Alumni**: 56 professionals found
- **AI/ML Experts**: Multiple professionals with AI/ML experience

## Dependencies
- **langgraph**: Simplified workflow orchestration (linear only)
- **aiohttp**: HTTP client for MCP server communication
- **typing**: Type hints for AgentState and tool interfaces
- **asyncio**: Async/await pattern for all operations

## Architecture Decisions
- **Simplified Over Complex**: Removed retry logic, quality assessment, and state management complexity
- **Linear Workflow**: No cyclical dependencies or checkpointers that caused serialization issues
- **Real Data Integration**: Direct MCP calls return actual results from Neo4j knowledge graph
- **Working Over Perfect**: Prioritized working implementation over sophisticated architecture

## Files Removed During Simplification
- Complex planners: `plan_generator.py`, `query_analyzer.py`
- Complex executors: `executor_node.py`, `plan_validator.py`
- Complex synthesizers: `quality_assessor.py`, `response_generator.py`
- Complex workflows: `retry_manager.py`, `main_workflow.py`, `workflow_nodes.py`
- Complex state: `enums.py`, `plan.py`, `manager.py`

## Next Steps
- Complete `agent_run.py` as main entry point
- Final cleanup of any remaining unused files
- Integration testing with full chatbot functionality