"""
Plan Validator Module

Validates execution plans before execution to ensure they are feasible.
This module focuses solely on plan validation and dependency checking.
"""

from typing import Dict, Any, List
from agent.state import AgentState


class PlanValidator:
    """
    Validates execution plans before execution to ensure they are feasible.
    
    Checks for proper step configuration, argument validation, and dependency resolution.
    """
    
    @classmethod
    def validate_plan(cls, state: AgentState) -> Dict[str, Any]:
        """
        Validate the execution plan in the current state.
        
        Args:
            state: Current agent state with execution plan
            
        Returns:
            Validation result with status and any issues found
        """
        
        if 'execution_plan' not in state:
            return {
                'valid': False,
                'error': 'No execution plan found in state',
                'issues': ['Missing execution plan']
            }
        
        plan = state['execution_plan']
        issues = []
        
        # Check if plan has steps
        if not plan.steps:
            issues.append('Execution plan has no steps')
        
        # Validate each step
        for step in plan.steps:
            step_issues = cls._validate_step(step)
            issues.extend(step_issues)
        
        # Check for circular dependencies
        if cls._has_circular_dependencies(plan.steps):
            issues.append('Circular dependencies detected in plan steps')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_steps': len(plan.steps),
            'critical_steps': len([s for s in plan.steps if s.critical])
        }
    
    @classmethod
    def _validate_step(cls, step) -> List[str]:
        """Validate a single plan step."""
        issues = []
        
        # Check required fields
        if not step.id:
            issues.append(f'Step missing ID')
        if not step.tool_name:
            issues.append(f'Step {step.id} missing tool name')
        if not isinstance(step.arguments, dict):
            issues.append(f'Step {step.id} has invalid arguments format')
        
        # Check tool name validity (basic check for known patterns)
        valid_tool_patterns = [
            'find_person', 'find_people', 'get_company', 'natural_language',
            'get_skill', 'find_colleagues', 'find_domain'
        ]
        
        if not any(pattern in step.tool_name for pattern in valid_tool_patterns):
            issues.append(f'Step {step.id} has potentially invalid tool name: {step.tool_name}')
        
        return issues
    
    @classmethod
    def _has_circular_dependencies(cls, steps) -> bool:
        """Check for circular dependencies in plan steps."""
        # Create dependency graph
        deps = {step.id: step.depends_on for step in steps}
        
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in deps.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in deps:
            if has_cycle(step_id):
                return True
        
        return False