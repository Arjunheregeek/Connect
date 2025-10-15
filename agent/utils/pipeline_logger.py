"""
Pipeline Logger - Comprehensive logging for LangGraph Agent Pipeline

Logs every input/output at every stage:
- Planner Node (QueryDecomposer + SubQueryGenerator)
- Executor Node (MCP Tool Calls)
- Synthesizer Node (Profile Fetch + GPT-4o)

Exports to CSV for analysis and debugging.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib


class PipelineLogger:
    """
    Comprehensive logger for agent pipeline.
    
    Logs structure:
    - query_id: Unique identifier for each query
    - timestamp: When the log was created
    - stage: planner/executor/synthesizer
    - module: Specific component (e.g., query_decomposer, mcp_tool, gpt4o)
    - operation: What happened (e.g., decompose, tool_call, synthesize)
    - input_data: Raw input (JSON)
    - output_data: Raw output (JSON)
    - metadata: Additional info (tokens, duration, etc.)
    """
    
    def __init__(self, output_dir: str = "logs"):
        """
        Initialize pipeline logger.
        
        Args:
            output_dir: Directory to save log files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Log storage
        self.logs: List[Dict[str, Any]] = []
        
        # CSV file paths
        self.master_log_file = self.output_dir / f"pipeline_master_{self.session_id}.csv"
        self.planner_log_file = self.output_dir / f"planner_{self.session_id}.csv"
        self.executor_log_file = self.output_dir / f"executor_{self.session_id}.csv"
        self.synthesizer_log_file = self.output_dir / f"synthesizer_{self.session_id}.csv"
        
        print(f"📊 Pipeline Logger initialized - Session: {self.session_id}")
        print(f"📁 Logs directory: {self.output_dir.absolute()}")
    
    def generate_query_id(self, query: str) -> str:
        """Generate unique ID for a query."""
        timestamp = datetime.now().isoformat()
        unique_string = f"{query}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def log(
        self,
        query_id: str,
        stage: str,
        module: str,
        operation: str,
        input_data: Any,
        output_data: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a pipeline step.
        
        Args:
            query_id: Unique query identifier
            stage: planner/executor/synthesizer
            module: Component name
            operation: What happened
            input_data: Input to the module
            output_data: Output from the module
            metadata: Additional metadata (tokens, duration, etc.)
        """
        log_entry = {
            'query_id': query_id,
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'module': module,
            'operation': operation,
            'input_data': self._serialize(input_data),
            'output_data': self._serialize(output_data),
            'metadata': json.dumps(metadata or {})
        }
        
        self.logs.append(log_entry)
        
        # Print to console for real-time debugging
        print(f"\n{'='*80}")
        print(f"📝 LOG: {stage.upper()} → {module} → {operation}")
        print(f"{'='*80}")
        print(f"🔹 Query ID: {query_id}")
        print(f"🔹 Timestamp: {log_entry['timestamp']}")
        
        if input_data:
            print(f"\n📥 INPUT:")
            self._print_data(input_data)
        
        if output_data:
            print(f"\n📤 OUTPUT:")
            self._print_data(output_data)
        
        if metadata:
            print(f"\n📊 METADATA:")
            for key, value in metadata.items():
                print(f"   - {key}: {value}")
        
        print(f"{'='*80}\n")
    
    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string."""
        if data is None:
            return ""
        
        try:
            # Handle common types
            if isinstance(data, (str, int, float, bool)):
                return str(data)
            elif isinstance(data, (dict, list)):
                return json.dumps(data, indent=2, default=str)
            else:
                return str(data)
        except Exception as e:
            return f"<Serialization Error: {str(e)}>"
    
    def _print_data(self, data: Any, indent: int = 3):
        """Pretty print data to console."""
        try:
            if isinstance(data, str):
                # Truncate very long strings
                if len(data) > 500:
                    print(f"{' '*indent}{data[:500]}...")
                else:
                    print(f"{' '*indent}{data}")
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        print(f"{' '*indent}{key}: {json.dumps(value, indent=2, default=str)[:200]}...")
                    else:
                        print(f"{' '*indent}{key}: {value}")
            elif isinstance(data, list):
                print(f"{' '*indent}[{len(data)} items]")
                for i, item in enumerate(data[:3]):  # Show first 3
                    print(f"{' '*indent}  [{i}]: {str(item)[:100]}...")
            else:
                print(f"{' '*indent}{str(data)[:200]}")
        except Exception as e:
            print(f"{' '*indent}<Print Error: {str(e)}>")
    
    def save_logs(self):
        """Save all logs to CSV files."""
        if not self.logs:
            print("⚠️  No logs to save")
            return
        
        # Save master log
        self._save_csv(self.master_log_file, self.logs)
        print(f"✅ Master log saved: {self.master_log_file}")
        
        # Save stage-specific logs
        planner_logs = [log for log in self.logs if log['stage'] == 'planner']
        executor_logs = [log for log in self.logs if log['stage'] == 'executor']
        synthesizer_logs = [log for log in self.logs if log['stage'] == 'synthesizer']
        
        if planner_logs:
            self._save_csv(self.planner_log_file, planner_logs)
            print(f"✅ Planner log saved: {self.planner_log_file}")
        
        if executor_logs:
            self._save_csv(self.executor_log_file, executor_logs)
            print(f"✅ Executor log saved: {self.executor_log_file}")
        
        if synthesizer_logs:
            self._save_csv(self.synthesizer_log_file, synthesizer_logs)
            print(f"✅ Synthesizer log saved: {self.synthesizer_log_file}")
        
        print(f"\n📊 Total logs saved: {len(self.logs)}")
    
    def _save_csv(self, filepath: Path, logs: List[Dict[str, Any]]):
        """Save logs to CSV file."""
        if not logs:
            return
        
        fieldnames = ['query_id', 'timestamp', 'stage', 'module', 'operation', 
                     'input_data', 'output_data', 'metadata']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(logs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of logged data."""
        if not self.logs:
            return {'total_logs': 0}
        
        stages = {}
        for log in self.logs:
            stage = log['stage']
            if stage not in stages:
                stages[stage] = 0
            stages[stage] += 1
        
        return {
            'total_logs': len(self.logs),
            'session_id': self.session_id,
            'stages': stages,
            'queries_processed': len(set(log['query_id'] for log in self.logs))
        }


# Global logger instance
_global_logger: Optional[PipelineLogger] = None


def get_logger(output_dir: str = "logs") -> PipelineLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = PipelineLogger(output_dir=output_dir)
    return _global_logger


def reset_logger(output_dir: str = "logs") -> PipelineLogger:
    """Reset global logger (create new session)."""
    global _global_logger
    _global_logger = PipelineLogger(output_dir=output_dir)
    return _global_logger


# Test function
if __name__ == "__main__":
    print("="*80)
    print("PIPELINE LOGGER - TEST")
    print("="*80)
    
    logger = PipelineLogger(output_dir="test_logs")
    query_id = logger.generate_query_id("Find Python developers")
    
    # Test planner logging
    logger.log(
        query_id=query_id,
        stage="planner",
        module="query_decomposer",
        operation="decompose",
        input_data={"query": "Find Python developers at Google"},
        output_data={
            "skill_filters": ["Python"],
            "company_filters": ["Google"]
        },
        metadata={"tokens_used": 150, "duration_ms": 500}
    )
    
    # Test executor logging
    logger.log(
        query_id=query_id,
        stage="executor",
        module="mcp_tool",
        operation="find_people_by_skill",
        input_data={"skill": "Python"},
        output_data={"person_ids": [123, 456, 789], "count": 3},
        metadata={"duration_ms": 250}
    )
    
    # Save logs
    logger.save_logs()
    
    # Print summary
    summary = logger.get_summary()
    print(f"\n📊 Summary:")
    print(json.dumps(summary, indent=2))
