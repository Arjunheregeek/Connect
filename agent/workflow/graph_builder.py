"""
ENHANCED LangGraph Builder

Creates an enhanced workflow with intelligent query processing:
Planning (QueryDecomposer + SubQueryGenerator) → Execution → Synthesis

Enhanced Features:
- Query decomposition into structured filters
- Sub-query generation with synonym expansion
- Multi-tool execution strategies
"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState

# Import enhanced nodes
from agent.nodes.planner.enhanced_planner_node import enhanced_planner_node
from agent.nodes.executor.enhanced_executor_node import enhanced_executor_node
from agent.nodes.synthesizer.enhanced_synthesizer_node import enhanced_synthesizer_node


class WorkflowGraphBuilder:
    """
    ENHANCED LangGraph builder with intelligent query processing.
    
    Enhanced Features:
    - QueryDecomposer: Extract structured filters from natural language
    - SubQueryGenerator: Generate sub-queries with synonym expansion
    - Multi-tool execution strategies
    
    Workflow:
    Start → Enhanced Planner → Enhanced Executor → Enhanced Synthesizer → End
    """
    
    @staticmethod
    def build_graph() -> StateGraph:
        """
        Build ENHANCED workflow graph with intelligent query processing.
        
        ENHANCED Workflow:
        Start → Enhanced Planner (QueryDecomposer + SubQueryGenerator) → 
                Enhanced Executor (Multi-tool execution) → 
                Enhanced Synthesizer (GPT-4o response generation) → End
        
        Returns:
            Compiled LangGraph workflow
        """
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add enhanced nodes
        workflow.add_node("planner", enhanced_planner_node)
        workflow.add_node("executor", enhanced_executor_node)
        workflow.add_node("synthesizer", enhanced_synthesizer_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add linear edges
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile(
            checkpointer=None  # No state persistence for simplicity
        )
        
        # COMMENTED OUT - PROBLEMATIC COMPLEXITY
        # =================================================================
        # # Add workflow nodes
        # workflow.add_node("planner", EnhancedWorkflowNodes.enhanced_planner_node)
        # workflow.add_node("executor", EnhancedWorkflowNodes.enhanced_executor_node)
        # workflow.add_node("synthesizer", EnhancedWorkflowNodes.enhanced_synthesizer_node)
        # workflow.add_node("re_planner", EnhancedWorkflowNodes.re_planner_node)
        # workflow.add_node("fallback", EnhancedWorkflowNodes.fallback_response_node)
        #
        # # Add conditional routing after executor
        # workflow.add_conditional_edges(
        #     "executor",
        #     EnhancedWorkflowNodes.quality_check_node,  # ❌ CYCLICAL COMPLEXITY
        #     {
        #         "re_plan": "re_planner",    # ❌ CREATES CYCLES
        #         "synthesize": "synthesizer", # Results are good, generate response
        #         "end": "fallback"           # Exhausted retries, generate fallback
        #     }
        # )
        #
        # # Re-planner goes back to executor (creating the cycle)
        # workflow.add_edge("re_planner", "executor")
        #
        # # Both synthesizer and fallback end the workflow
        # workflow.add_edge("synthesizer", END)
        # workflow.add_edge("fallback", END)
        
        return workflow.compile(
            checkpointer=None  # No state persistence for simplicity
        )
    
    @staticmethod
    def get_workflow_diagram() -> str:
        """
        Get a text representation of the enhanced workflow diagram.
        
        Returns:
            ASCII diagram of the workflow
        """
        
        return """
ENHANCED LANGGRAPH WORKFLOW
===========================

┌─────────────────────────────────────┐
│             START                   │
│        (User Query)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      ENHANCED PLANNER               │
│                                     │
│  Step 1: QueryDecomposer            │
│  ├─ Natural Language → Filters      │
│  └─ Extract: skills, companies,     │
│              locations, experience  │
│                                     │
│  Step 2: SubQueryGenerator          │
│  ├─ Filters → Sub-queries           │
│  ├─ Synonym expansion               │
│  ├─ Multi-tool strategies           │
│  └─ Priority assignment             │
│                                     │
│  Output: sub_queries + strategy     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      ENHANCED EXECUTOR              │
│                                     │
│  - Read sub_queries from state      │
│  - Execute via MCP tools            │
│  - Handle parallel/sequential       │
│  - Extract person IDs               │
│  - Aggregate results                │
│                                     │
│  Output: accumulated_data (IDs)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     ENHANCED SYNTHESIZER            │
│                                     │
│  - Fetch complete profiles (MCP)    │
│  - Rank by relevance                │
│  - Generate response (GPT-4o)       │
│  - Format with contact info         │
│                                     │
│  Output: natural language response  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│             END                     │
│   (Human-readable response)         │
└─────────────────────────────────────┘

Key Features:
- Intelligent query decomposition
- Synonym expansion for better recall
- Multi-tool execution strategies
- Priority-based sub-query execution
- Complete profile retrieval
- GPT-4o powered response generation
        """