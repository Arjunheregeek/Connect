#!/usr/bin/env python3
"""
Instrumented Agent Runner - Full Pipeline Logging (V2 - Fixed)

This version logs EVERY input/output at EVERY stage WITHOUT breaking the workflow.
Uses a simpler approach - wrapping at the workflow level instead of monkey-patching.

Usage:
    python app/agent_run_instrumented_v2.py "Find Python developers at Google"
"""

import asyncio
import sys
import time
import json
from typing import Dict, Any, List
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.workflow.graph_builder import WorkflowGraphBuilder
from agent.state.types import AgentState
from agent.utils.pipeline_logger import get_logger, reset_logger

# Import the actual node functions
from agent.nodes.planner.enhanced_planner_node import enhanced_planner_node
from agent.nodes.executor.enhanced_executor_node import enhanced_executor_node
from agent.nodes.synthesizer.enhanced_synthesizer_node import enhanced_synthesizer_node


class InstrumentedConnectAgent:
    """Enhanced Connect Agent with comprehensive logging."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the instrumented agent."""
        print("🚀 Initializing Instrumented Connect Agent (V2)...")
        print("📊 Full pipeline logging enabled")
        
        # Initialize logger
        self.logger = reset_logger(output_dir=log_dir)
        
        # Use standard workflow builder - DON'T modify it
        self.workflow_builder = WorkflowGraphBuilder()
        self.workflow = self.workflow_builder.build_graph()
        
        self.session_history: List[Dict[str, Any]] = []
        print("✅ Instrumented agent ready!")
    
    async def ask(self, question: str) -> str:
        """Ask a question with full logging."""
        print(f"\n{'='*80}")
        print(f"🔍 PROCESSING QUERY: {question}")
        print(f"{'='*80}\n")
        
        # Generate query ID
        query_id = self.logger.generate_query_id(question)
        print(f"🆔 Query ID: {query_id}\n")
        
        # Store query_id for access
        self.logger._current_query_id = query_id
        
        # Log the initial query
        self.logger.log(
            query_id=query_id,
            stage="input",
            module="user",
            operation="query",
            input_data={"question": question}
        )
        
        # Create initial state
        initial_state: AgentState = {
            'user_query': question,
            'session_id': f"instrumented-v2-{int(time.time())}",
            'workflow_status': 'initialized',
            'messages': [],
            'accumulated_data': [],
            'tool_results': [],
            'errors': [],
            'tools_used': [],
            'filters': {},
            'sub_queries': [],
            'execution_strategy': 'parallel_union',
            'planning_metadata': {},
            'final_response': '',
            'desired_count': 5
        }
        
        try:
            start_time = time.time()
            
            # Run workflow WITH manual node logging
            result = await self._run_workflow_with_logging(initial_state, query_id)
            
            execution_time = time.time() - start_time
            
            # Log final result
            self.logger.log(
                query_id=query_id,
                stage="output",
                module="workflow",
                operation="complete",
                input_data={"question": question},
                output_data={
                    "final_response": result.get('final_response', '')[:500],
                    "workflow_status": result.get('workflow_status'),
                    "person_count": len(result.get('accumulated_data', [])),
                    "tools_used": result.get('tools_used', [])
                },
                metadata={
                    "total_execution_time": execution_time,
                    "sub_queries_executed": len(result.get('sub_queries', [])),
                    "tool_calls": len(result.get('tool_results', []))
                }
            )
            
            # Save logs after each query
            self.logger.save_logs()
            
            # Print summary
            print(f"\n{'='*80}")
            print(f"✅ QUERY COMPLETE")
            print(f"{'='*80}")
            print(f"⏱️  Total Time: {execution_time:.2f}s")
            print(f"🔧 Tools Used: {len(result.get('tool_results', []))}")
            print(f"👥 People Found: {len(result.get('accumulated_data', []))}")
            print(f"📊 Logs Saved: {self.logger.get_summary()['total_logs']} entries")
            print(f"{'='*80}\n")
            
            return result.get('final_response', 'No response generated.')
            
        except Exception as e:
            # Log error
            self.logger.log(
                query_id=query_id,
                stage="error",
                module="workflow",
                operation="exception",
                input_data={"question": question},
                output_data={"error": str(e)},
                metadata={"exception_type": type(e).__name__}
            )
            
            self.logger.save_logs()
            raise
    
    async def _run_workflow_with_logging(self, initial_state: AgentState, query_id: str) -> AgentState:
        """Run the workflow with manual logging at each stage."""
        state = initial_state
        
        # Stage 1: Planner
        print(f"{'='*80}")
        print("🎯 STAGE 1: PLANNER")
        print(f"{'='*80}")
        self.logger.log(
            query_id=query_id,
            stage="planner",
            module="workflow",
            operation="planner_start",
            input_data={"user_query": state.get('user_query')}
        )
        start = time.time()
        state = await enhanced_planner_node(state)
        duration = time.time() - start
        self.logger.log(
            query_id=query_id,
            stage="planner",
            module="workflow",
            operation="planner_complete",
            input_data={"user_query": state.get('user_query')},
            output_data={
                "filters": state.get('filters', {}),
                "sub_queries_count": len(state.get('sub_queries', [])),
                "execution_strategy": state.get('execution_strategy')
            },
            metadata={"duration_sec": duration}
        )
        
        # Stage 2: Executor
        print(f"\n{'='*80}")
        print("⚡ STAGE 2: EXECUTOR")
        print(f"{'='*80}")
        self.logger.log(
            query_id=query_id,
            stage="executor",
            module="workflow",
            operation="executor_start",
            input_data={
                "sub_queries_count": len(state.get('sub_queries', [])),
                "execution_strategy": state.get('execution_strategy')
            }
        )
        start = time.time()
        state = await enhanced_executor_node(state)
        duration = time.time() - start
        self.logger.log(
            query_id=query_id,
            stage="executor",
            module="workflow",
            operation="executor_complete",
            input_data={
                "sub_queries_count": len(state.get('sub_queries', [])),
            },
            output_data={
                "person_count": len(state.get('accumulated_data', [])),
                "tool_results_count": len(state.get('tool_results', []))
            },
            metadata={"duration_sec": duration}
        )
        
        # Stage 3: Synthesizer
        print(f"\n{'='*80}")
        print("✨ STAGE 3: SYNTHESIZER")
        print(f"{'='*80}")
        self.logger.log(
            query_id=query_id,
            stage="synthesizer",
            module="workflow",
            operation="synthesizer_start",
            input_data={
                "user_query": state.get('user_query'),
                "person_count": len(state.get('accumulated_data', [])),
                "desired_count": state.get('desired_count', 5)
            }
        )
        start = time.time()
        state = await enhanced_synthesizer_node(state)
        duration = time.time() - start
        self.logger.log(
            query_id=query_id,
            stage="synthesizer",
            module="workflow",
            operation="synthesizer_complete",
            input_data={
                "user_query": state.get('user_query'),
                "person_count": len(state.get('accumulated_data', []))
            },
            output_data={
                "final_response_preview": state.get('final_response', '')[:200],
                "workflow_status": state.get('workflow_status'),
                "profiles_fetched": state.get('synthesizer_metadata', {}).get('profiles_fetched', 0)
            },
            metadata={
                "duration_sec": duration,
                "token_usage": state.get('synthesizer_metadata', {}).get('token_usage', 0)
            }
        )
        
        return state


async def main():
    """Main entry point for instrumented agent."""
    if len(sys.argv) < 2:
        print("""
🤖 Instrumented Connect Agent V2 - Full Pipeline Logging

Usage:
    python app/agent_run_instrumented_v2.py "your question"

Examples:
    python app/agent_run_instrumented_v2.py "Find Python developers at Google"
    python app/agent_run_instrumented_v2.py "AI experts in Bangalore with 5+ years"

All logs will be saved to the 'logs/' directory with CSV files for analysis.
        """)
        return
    
    question = ' '.join(sys.argv[1:])
    
    # Create instrumented agent
    agent = InstrumentedConnectAgent(log_dir="logs")
    
    # Ask question
    response = await agent.ask(question)
    
    print(f"\n{'='*80}")
    print("📝 FINAL RESPONSE")
    print(f"{'='*80}")
    print(response)
    print(f"{'='*80}\n")
    
    # Print log summary
    summary = agent.logger.get_summary()
    print("📊 Logging Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
