"""
LangGraph Builder

Constructs the cyclical workflow graph with proper routing and state management.
"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
from .workflow_nodes import EnhancedWorkflowNodes


class WorkflowGraphBuilder:
    """
    Builds the LangGraph workflow with cyclical retry logic.
    """
    
    @staticmethod
    def build_graph() -> StateGraph:
        """
        Build the complete LangGraph workflow with cyclical retry logic.
        
        Workflow:
        Start → Planner → Executor → Quality Check → {Re-plan | Synthesizer | Fallback} → End
        
        Returns:
            Compiled LangGraph workflow
        """
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add workflow nodes
        workflow.add_node("planner", EnhancedWorkflowNodes.enhanced_planner_node)
        workflow.add_node("executor", EnhancedWorkflowNodes.enhanced_executor_node)
        workflow.add_node("synthesizer", EnhancedWorkflowNodes.enhanced_synthesizer_node)
        workflow.add_node("re_planner", EnhancedWorkflowNodes.re_planner_node)
        workflow.add_node("fallback", EnhancedWorkflowNodes.fallback_response_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add edges
        workflow.add_edge("planner", "executor")
        
        # Add conditional routing after executor
        workflow.add_conditional_edges(
            "executor",
            EnhancedWorkflowNodes.quality_check_node,
            {
                "re_plan": "re_planner",    # Try again with different strategy
                "synthesize": "synthesizer", # Results are good, generate response
                "end": "fallback"           # Exhausted retries, generate fallback
            }
        )
        
        # Re-planner goes back to executor (creating the cycle)
        workflow.add_edge("re_planner", "executor")
        
        # Both synthesizer and fallback end the workflow
        workflow.add_edge("synthesizer", END)
        workflow.add_edge("fallback", END)
        
        return workflow.compile(
            checkpointer=None,
            interrupt_before=None,
            interrupt_after=None,
            debug=False
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