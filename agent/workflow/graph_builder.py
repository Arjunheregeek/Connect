"""
SIMPLIFIED LangGraph Builder

Creates a simple linear workflow: Planning → Execution → Synthesis
Removes all cyclical logic, quality assessment, and retry complexity.
"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
# SIMPLIFIED: Import simplified nodes that avoid all problematic complexity
from agent.nodes.planner.simple_planner import simple_planner_node
from agent.nodes.executor.simple_executor import simple_executor_node  
from agent.nodes.synthesizer.simple_synthesizer import simple_synthesizer_node


class WorkflowGraphBuilder:
    """
    SIMPLIFIED LangGraph builder - linear workflow only.
    
    Removes all problematic features:
    - Cyclical routing
    - Quality assessment 
    - Retry logic
    - Enhanced wrapper nodes
    """
    
    @staticmethod
    def build_graph() -> StateGraph:
        """
        Build SIMPLE linear workflow graph.
        
        SIMPLIFIED Workflow:
        Start → Planner → Executor → Synthesizer → End
        
        No cycles, no quality checks, no retry logic - just linear execution.
        
        Returns:
            Compiled LangGraph workflow
        """
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add ONLY the simplified nodes - no complex wrappers
        workflow.add_node("planner", simple_planner_node)
        workflow.add_node("executor", simple_executor_node)
        workflow.add_node("synthesizer", simple_synthesizer_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add SIMPLE linear edges only
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
            # Remove checkpointer to avoid serialization issues
            checkpointer=None  # SIMPLIFIED: No state persistence
        )
    
    @staticmethod
    def get_workflow_diagram() -> str:
        """
        Get a text representation of the workflow diagram.
        
        Returns:
            ASCII diagram of the workflow
        """
        
        return """
┌─────────────┐
│    Start    │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Planner   │◄─────────────┐
└─────┬───────┘              │
      │                      │
      ▼                      │
┌─────────────┐              │
│  Executor   │              │
└─────┬───────┘              │
      │                      │
      ▼                      │
┌─────────────┐              │
│ Quality     │              │
│ Check       │              │
└─────┬───────┘              │
      │                      │
      ▼                      │
 ┌──────────┐                │
 │ Decision │                │
 └────┬─────┘                │
      │                      │
   ┌──┴──┐                   │
   │     │                   │
   ▼     ▼                   │
┌─────────────┐              │
│ Re-planner  │──────────────┘
└─────────────┘
   │
   ▼
┌─────────────┐
│Synthesizer  │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Fallback  │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│     End     │
└─────────────┘

Flow Logic:
- Quality Check decides: re_plan | synthesize | end
- re_plan → Re-planner → Executor (creates cycle)
- synthesize → Synthesizer → End
- end → Fallback → End
        """