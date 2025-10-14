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

# Try to import enhanced planner, fallback to simple if not available
# Try to import enhanced nodes, fallback to simple if not available
try:
    from agent.nodes.planner.enhanced_planner_node import enhanced_planner_node
    ENHANCED_PLANNER_AVAILABLE = True
except ImportError:
    from agent.nodes.planner.simple_planner import simple_planner_node
    enhanced_planner_node = simple_planner_node
    ENHANCED_PLANNER_AVAILABLE = False

try:
    from agent.nodes.executor.enhanced_executor_node import enhanced_executor_node
    ENHANCED_EXECUTOR_AVAILABLE = True
except ImportError:
    from agent.nodes.executor.simple_executor import simple_executor_node
    enhanced_executor_node = simple_executor_node
    ENHANCED_EXECUTOR_AVAILABLE = False

from agent.nodes.synthesizer.simple_synthesizer import simple_synthesizer_node


class WorkflowGraphBuilder:
    """
    ENHANCED LangGraph builder with intelligent query processing.
    
    Enhanced Features:
    - QueryDecomposer: Extract structured filters from natural language
    - SubQueryGenerator: Generate sub-queries with synonym expansion
    - Multi-tool execution strategies
    
    Workflow:
    Start → Enhanced Planner → Executor → Synthesizer → End
    """
    
    @staticmethod
    def build_graph() -> StateGraph:
        """
        Build ENHANCED workflow graph with intelligent query processing.
        
        ENHANCED Workflow:
        Start → Enhanced Planner (QueryDecomposer + SubQueryGenerator) → 
                Executor (Multi-tool execution) → 
                Synthesizer (Result aggregation) → End
        
        Returns:
            Compiled LangGraph workflow
        """
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes - use enhanced nodes if available
        planner_node = enhanced_planner_node if ENHANCED_PLANNER_AVAILABLE else simple_planner_node
        executor_node = enhanced_executor_node if ENHANCED_EXECUTOR_AVAILABLE else simple_executor_node
        
        workflow.add_node("planner", planner_node)
        workflow.add_node("executor", executor_node)
        workflow.add_node("synthesizer", simple_synthesizer_node)
        
        # Log which components are being used
        if ENHANCED_PLANNER_AVAILABLE:
            print("✓ Using Enhanced Planner (QueryDecomposer + SubQueryGenerator)")
        else:
            print("⚠️  Enhanced Planner not available, using Simple Planner")
        
        if ENHANCED_EXECUTOR_AVAILABLE:
            print("✓ Using Enhanced Executor (Multi-tool with priority handling)")
        else:
            print("⚠️  Enhanced Executor not available, using Simple Executor")
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add linear edges
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
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
│         EXECUTOR                    │
│                                     │
│  - Read sub_queries from state      │
│  - Execute via MCP tools            │
│  - Handle parallel/sequential       │
│  - Aggregate results                │
│                                     │
│  Output: tool_results               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       SYNTHESIZER                   │
│                                     │
│  - Combine tool results             │
│  - Generate final response          │
│                                     │
│  Output: final_response             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│             END                     │
└─────────────────────────────────────┘

Key Features:
- Intelligent query decomposition
- Synonym expansion for better recall
- Multi-tool execution strategies
- Priority-based sub-query execution
        """