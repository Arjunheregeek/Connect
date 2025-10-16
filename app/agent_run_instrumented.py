#!/usr/bin/env python3
"""
Instrumented Agent Runner - Full Pipeline Logging

This version logs EVERY input/output at EVERY stage:
- Planner: QueryDecomposer + SubQueryGenerator  
- Executor: Each MCP tool call
- Synthesizer: Profile fetch + GPT-4o

All logs saved to CSV for analysis.

Usage:
    python app/agent_run_instrumented.py "Find Python developers at Google"
"""

import asyncio
import sys
import time
import json
from typing import Dict, Any, List
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CRITICAL: Patch nodes BEFORE any imports that use them
from agent.utils.pipeline_logger import get_logger, reset_logger

# Patch synthesizer BEFORE WorkflowGraphBuilder imports it
from agent.nodes.synthesizer.enhanced_synthesizer_node import enhanced_synthesizer_node as _original_synth
import agent.nodes.synthesizer.enhanced_synthesizer_node as synth_mod

async def _logged_synthesizer(state):
    """Logged wrapper for synthesizer"""
    query_id = getattr(get_logger(), '_current_query_id', 'unknown')
    get_logger().log(
        query_id=query_id,
        stage="synthesizer",
        module="synthesizer_node",
        operation="synthesize_input",
        input_data={
            "user_query": state.get('user_query'),
            "person_count": len(state.get('accumulated_data', [])),
            "desired_count": state.get('desired_count', 5)
        }
    )
    start_time = time.time()
    result = await _original_synth(state)
    duration = time.time() - start_time
    get_logger().log(
        query_id=query_id,
        stage="synthesizer",
        module="synthesizer_node",
        operation="synthesize_output",
        input_data={"user_query": state.get('user_query')},
        output_data={
            "final_response_preview": (result.get('final_response', '')[:200] + "...") if len(result.get('final_response', '')) > 200 else result.get('final_response', ''),
            "workflow_status": result.get('workflow_status'),
            "profiles_fetched": result.get('synthesizer_metadata', {}).get('profiles_fetched', 0)
        },
        metadata={
            "duration_sec": duration,
            "token_usage": result.get('synthesizer_metadata', {}).get('token_usage', 0)
        }
    )
    return result

synth_mod.enhanced_synthesizer_node = _logged_synthesizer

# NOW import WorkflowGraphBuilder (it will use the patched version)
from agent.workflow.graph_builder import WorkflowGraphBuilder
from agent.state.types import AgentState


class InstrumentedConnectAgent:
    """Enhanced Connect Agent with comprehensive logging."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the instrumented agent."""
        print("🚀 Initializing Instrumented Connect Agent...")
        print("📊 Full pipeline logging enabled")
        
        # Initialize logger
        self.logger = reset_logger(output_dir=log_dir)
        
        # **IMPORTANT: Patch nodes BEFORE building workflow**
        self._patch_nodes_before_build()
        
        # Initialize workflow (this imports the nodes)
        self.workflow_builder = WorkflowGraphBuilder()
        self.workflow = self.workflow_builder.build_graph()
        
        self.session_history: List[Dict[str, Any]] = []
        print("✅ Instrumented agent ready!")
    
    def _patch_nodes_before_build(self):
        """Patch all nodes BEFORE workflow is built."""
        print("🔧 Instrumenting workflow nodes with logging...")
        self._patch_planner_node()
        self._patch_executor_node()
        self._patch_synthesizer_node()
    
    def _patch_planner_node(self):
        """Patch planner node to add logging."""
        try:
            from agent.nodes.planner import enhanced_planner_node as planner_module
            from agent.nodes.planner.query_decomposer import QueryDecomposer
            from agent.nodes.planner.subquery_generator import SubQueryGenerator
            
            # Store original methods
            original_decompose = QueryDecomposer.decompose
            original_generate = SubQueryGenerator.generate
            
            # Create wrapped version
            def logged_decompose(self, query: str, max_retries: int = 2):
                """Wrapped decompose with logging."""
                query_id = getattr(self, '_current_query_id', 'unknown')
                
                # Log input
                get_logger().log(
                    query_id=query_id,
                    stage="planner",
                    module="query_decomposer",
                    operation="decompose_input",
                    input_data={"query": query, "max_retries": max_retries},
                    metadata={"model": self.model}
                )
                
                # Call original
                start_time = time.time()
                result = original_decompose(self, query, max_retries)
                duration = time.time() - start_time
                
                # Log output
                get_logger().log(
                    query_id=query_id,
                    stage="planner",
                    module="query_decomposer",
                    operation="decompose_output",
                    input_data={"query": query},
                    output_data=result,
                    metadata={
                        "duration_sec": duration,
                        "tokens_used": result.get('meta', {}).get('tokens_used', 0)
                    }
                )
                
                return result
            
            def logged_generate(self, filters: Dict[str, Any], max_retries: int = 2):
                """Wrapped generate with logging."""
                query_id = getattr(self, '_current_query_id', 'unknown')
                
                # Log input
                get_logger().log(
                    query_id=query_id,
                    stage="planner",
                    module="subquery_generator",
                    operation="generate_input",
                    input_data=filters,
                    metadata={"model": self.model}
                )
                
                # Call original
                start_time = time.time()
                result = original_generate(self, filters, max_retries)
                duration = time.time() - start_time
                
                # Log output
                get_logger().log(
                    query_id=query_id,
                    stage="planner",
                    module="subquery_generator",
                    operation="generate_output",
                    input_data=filters,
                    output_data=result,
                    metadata={
                        "duration_sec": duration,
                        "tokens_used": result.get('meta', {}).get('tokens_used', 0),
                        "sub_query_count": len(result.get('sub_queries', []))
                    }
                )
                
                return result
            
            # Patch the methods
            QueryDecomposer.decompose = logged_decompose
            SubQueryGenerator.generate = logged_generate
            
            print("✅ Planner node instrumented")
        except Exception as e:
            print(f"⚠️  Could not instrument planner: {e}")
    
    def _patch_executor_node(self):
        """Patch executor node to add logging."""
        try:
            from agent.mcp_client.mcp_client import MCPClient
            from agent.mcp_client.tool_client import MCPToolClient
            
            # We'll patch the tool_client methods to log each MCP call
            # Store original __getattribute__
            original_getattr = MCPToolClient.__getattribute__
            
            def logged_getattr(self, name):
                """Intercept tool calls to add logging."""
                attr = original_getattr(self, name)
                
                # If it's a coroutine (async method), wrap it
                if asyncio.iscoroutinefunction(attr) and not name.startswith('_'):
                    async def logged_tool_call(*args, **kwargs):
                        query_id = getattr(self, '_current_query_id', 'unknown')
                        
                        # Log input
                        get_logger().log(
                            query_id=query_id,
                            stage="executor",
                            module="mcp_tool",
                            operation=f"{name}_input",
                            input_data={"args": args, "kwargs": kwargs},
                            metadata={"tool_name": name}
                        )
                        
                        # Call original
                        start_time = time.time()
                        result = await attr(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        # Log output
                        get_logger().log(
                            query_id=query_id,
                            stage="executor",
                            module="mcp_tool",
                            operation=f"{name}_output",
                            input_data={"args": args, "kwargs": kwargs},
                            output_data={
                                "success": result.success,
                                "has_data": result.data is not None,
                                "error": result.error
                            },
                            metadata={
                                "tool_name": name,
                                "duration_sec": duration
                            }
                        )
                        
                        return result
                    
                    return logged_tool_call
                
                return attr
            
            # Patch
            MCPToolClient.__getattribute__ = logged_getattr
            
            print("✅ Executor node instrumented")
        except Exception as e:
            print(f"⚠️  Could not instrument executor: {e}")
    
    def _patch_synthesizer_node(self):
        """Patch synthesizer node to add logging."""
        try:
            # Import the actual function from the module
            from agent.nodes.synthesizer.enhanced_synthesizer_node import enhanced_synthesizer_node as original_synthesizer
            
            # Create wrapper
            async def logged_synthesizer(state):
                """Wrapped synthesizer with logging."""
                query_id = getattr(get_logger(), '_current_query_id', 'unknown')
                
                # Log input
                get_logger().log(
                    query_id=query_id,
                    stage="synthesizer",
                    module="synthesizer_node",
                    operation="synthesize_input",
                    input_data={
                        "user_query": state.get('user_query'),
                        "person_count": len(state.get('accumulated_data', [])),
                        "desired_count": state.get('desired_count', 5),
                        "filters": state.get('filters', {})
                    },
                    metadata={
                        "tool_results_count": len(state.get('tool_results', []))
                    }
                )
                
                # Call original
                start_time = time.time()
                result = await original_synthesizer(state)
                duration = time.time() - start_time
                
                # Log output
                get_logger().log(
                    query_id=query_id,
                    stage="synthesizer",
                    module="synthesizer_node",
                    operation="synthesize_output",
                    input_data={
                        "user_query": state.get('user_query'),
                        "person_count": len(state.get('accumulated_data', []))
                    },
                    output_data={
                        "final_response": result.get('final_response', '')[:500] if result.get('final_response') else '',
                        "workflow_status": result.get('workflow_status'),
                        "profiles_fetched": result.get('synthesizer_metadata', {}).get('profiles_fetched', 0)
                    },
                    metadata={
                        "duration_sec": duration,
                        "token_usage": result.get('synthesizer_metadata', {}).get('token_usage', 0),
                        "response_length": len(result.get('final_response', ''))
                    }
                )
                
                return result
            
            # Patch the module - need to patch where it's imported in graph_builder
            import agent.nodes.synthesizer.enhanced_synthesizer_node as synth_module
            synth_module.enhanced_synthesizer_node = logged_synthesizer
            
            # Also patch in the graph_builder imports
            from agent.nodes.synthesizer import enhanced_synthesizer_node as synth_init_module
            synth_init_module.enhanced_synthesizer_node = logged_synthesizer
            
            # Also try to patch OpenAI if possible (for when profiles are found)
            try:
                from openai import OpenAI
                original_create = OpenAI.chat.completions.create
                
                def logged_create(self, **kwargs):
                    """Wrapped GPT-4o call with logging."""
                    query_id = getattr(get_logger(), '_current_query_id', 'unknown')
                    
                    # Log input
                    get_logger().log(
                        query_id=query_id,
                        stage="synthesizer",
                        module="gpt4o",
                        operation="chat_completion_input",
                        input_data={
                            "model": kwargs.get('model'),
                            "messages_count": len(kwargs.get('messages', [])),
                            "temperature": kwargs.get('temperature'),
                            "max_tokens": kwargs.get('max_tokens')
                        },
                        metadata={"model": kwargs.get('model')}
                    )
                    
                    # Call original
                    start_time = time.time()
                    result = original_create(self, **kwargs)
                    duration = time.time() - start_time
                    
                    # Log output
                    get_logger().log(
                        query_id=query_id,
                        stage="synthesizer",
                        module="gpt4o",
                        operation="chat_completion_output",
                        input_data={"model": kwargs.get('model')},
                        output_data={
                            "response_preview": result.choices[0].message.content[:200] + "..." if len(result.choices[0].message.content) > 200 else result.choices[0].message.content,
                            "finish_reason": result.choices[0].finish_reason
                        },
                        metadata={
                            "duration_sec": duration,
                            "tokens_used": result.usage.total_tokens,
                            "prompt_tokens": result.usage.prompt_tokens,
                            "completion_tokens": result.usage.completion_tokens
                        }
                    )
                    
                    return result
                
                # Patch
                OpenAI.chat.completions.create = logged_create
            except Exception as e:
                print(f"   ℹ️  GPT-4o logging disabled: {e}")
            
            print("✅ Synthesizer node instrumented")
        except Exception as e:
            print(f"⚠️  Could not instrument synthesizer: {e}")
    
    async def ask(self, question: str) -> str:
        """Ask a question with full logging."""
        print(f"\n{'='*80}")
        print(f"🔍 PROCESSING QUERY: {question}")
        print(f"{'='*80}\n")
        
        # Generate query ID
        query_id = self.logger.generate_query_id(question)
        print(f"🆔 Query ID: {query_id}\n")
        
        # Store query_id in context for the patches to access
        # We'll add it to the logger itself as a hack
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
            'session_id': f"instrumented-{int(time.time())}",
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
            
            # Run workflow
            result = await self.workflow.ainvoke(initial_state)
            
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


async def main():
    """Main entry point for instrumented agent."""
    if len(sys.argv) < 2:
        print("""
🤖 Instrumented Connect Agent - Full Pipeline Logging

Usage:
    python app/agent_run_instrumented.py "your question"

Examples:
    python app/agent_run_instrumented.py "Find Python developers at Google"
    python app/agent_run_instrumented.py "AI experts in Bangalore with 5+ years"

All logs will be saved to the 'logs/' directory with CSV files for:
- Master log (all stages combined)
- Planner log (QueryDecomposer + SubQueryGenerator)
- Executor log (MCP tool calls)
- Synthesizer log (Profile fetch + GPT-4o)
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
