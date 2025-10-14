"""
SubQuery Generator - Step 2 of Enhanced Query Processing

Generates intelligent sub-queries from extracted filters with:
- Synonym/variation expansion for skills and roles
- Multiple search strategies (skill arrays, job descriptions, titles)
- Smart tool mapping from the 19 available MCP tools
- Priority assignment for execution order

Workflow:
1. Query Decomposer → Filters → This SubQuery Generator
2. SubQuery Generator → Sub-queries with tool mappings → Multi-Tool Executor (next file)
"""

import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import tool catalog for tool validation and query decomposer for integration
TOOL_CATALOG = []
QueryDecomposer = None

def get_all_tool_names():
    return []

# Try multiple import strategies
import sys
from pathlib import Path

# Add project root to path if not already there
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    # Try relative import first (when used as module)
    from .tool_catalog import TOOL_CATALOG, get_all_tool_names
    from .query_decomposer import QueryDecomposer
    print("✓ Loaded via relative import")
except ImportError as e1:
    try:
        # Try absolute import (when run as script)
        from agent.nodes.planner.tool_catalog import TOOL_CATALOG as TC
        from agent.nodes.planner.tool_catalog import get_all_tool_names as get_tools
        from agent.nodes.planner.query_decomposer import QueryDecomposer as QD
        TOOL_CATALOG = TC
        get_all_tool_names = get_tools
        QueryDecomposer = QD
        print("✓ Loaded via absolute import")
    except ImportError as e2:
        print(f"⚠️  Import warnings: {e1}, {e2}")
        print("⚠️  Running in standalone mode without query_decomposer integration")


class SubQueryGenerator:
    """
    Generates intelligent sub-queries from extracted filters.
    
    Key Features:
    - Synonym expansion (Python → Python developer, Python engineer, Python programming)
    - Multiple tool strategies (skill arrays + job descriptions + titles)
    - Role interpretation (founder → leadership indicators, entrepreneur keywords)
    - Smart tool selection from 19 available MCP tools
    
    Example:
        Input: {
            "skill_filters": ["Python"],
            "company_filters": ["Google"],
            "other_criteria": {"role": "founder"}
        }
        
        Output: [
            {
                "sub_query": "Find people with Python in technical skills",
                "tool": "find_people_by_skill",
                "params": {"skill": "Python"},
                "priority": 1,
                "rationale": "Direct skill match in skill arrays"
            },
            {
                "sub_query": "Find people with Python development experience in job descriptions",
                "tool": "search_job_descriptions_by_keywords",
                "params": {"keywords": ["Python", "Python developer", "Python engineer"], "match_type": "any"},
                "priority": 1,
                "rationale": "Contextual skill search in job history"
            },
            ...
        ]
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize SubQuery Generator.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-4o)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.available_tools = get_all_tool_names()
    
    def generate(
        self,
        filters: Dict[str, Any],
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate sub-queries from extracted filters.
        
        Args:
            filters: Output from QueryDecomposer.decompose()
            max_retries: Maximum retry attempts if generation fails
            
        Returns:
            Dictionary with:
            {
                "original_query": str,
                "filters_used": Dict,
                "sub_queries": List[Dict],
                "execution_strategy": str,
                "total_sub_queries": int,
                "meta": Dict
            }
        """
        if not filters or not any([
            filters.get("skill_filters"),
            filters.get("company_filters"),
            filters.get("location_filters"),
            filters.get("name_filters"),
            filters.get("institution_filters"),
            filters.get("other_criteria")
        ]):
            return self._empty_result(filters, "No filters to generate sub-queries from")
        
        prompt = self._create_generation_prompt(filters)
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at generating intelligent search sub-queries with synonym expansion and multi-strategy approaches. Always return valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.4,  # Slightly higher for creative synonym generation
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content.strip()
                result = json.loads(content)
                
                # Validate and normalize
                validated = self._validate_and_normalize(result, filters)
                
                # Add metadata
                validated["meta"] = {
                    "model": self.model,
                    "attempt": attempt + 1,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
                
                return validated
                
            except Exception as e:
                if attempt < max_retries:
                    continue
                return self._empty_result(filters, f"Generation failed: {str(e)}")
    
    def _create_generation_prompt(self, filters: Dict[str, Any]) -> str:
        """Create the LLM prompt for sub-query generation."""
        
        # Build tool catalog summary
        tool_summary = []
        for tool in TOOL_CATALOG:
            tool_summary.append(f"- {tool['name']}: {tool['description'][:100]}...")
        tools_text = "\n".join(tool_summary) if tool_summary else "19 tools available"
        
        prompt = f"""You are generating intelligent sub-queries for a professional network search system.

AVAILABLE TOOLS (19 total):
{tools_text}

YOUR TASK:
Generate 2-6 sub-queries from the extracted filters using MULTIPLE SEARCH STRATEGIES:

1. **SYNONYM EXPANSION**: Expand skills/roles with variations
   - Python → ["Python", "Python developer", "Python engineer", "Python programming"]
   - AI → ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning"]
   - Founder → ["Founder", "Co-founder", "CEO", "Entrepreneur", "Startup founder"]

2. **MULTI-TOOL STRATEGY**: Use multiple tools for comprehensive search
   - Skill search: Use BOTH find_people_by_skill (skill arrays) AND search_job_descriptions_by_keywords (job history)
   - Role search: Use find_leadership_indicators + search_job_descriptions_by_keywords
   - Company search: Use find_people_by_company + get_company_employees

3. **SMART TOOL SELECTION**: Pick the right tool for each filter
   - Skills → find_people_by_skill, find_people_with_multiple_skills, search_job_descriptions_by_keywords
   - Companies → find_people_by_company, get_company_employees
   - Locations → find_people_by_location
   - Names → find_person_by_name, get_person_details
   - Institutions → find_people_by_institution
   - Experience → find_people_by_experience_level
   - Leadership/Roles → find_leadership_indicators, search_job_descriptions_by_keywords

EXTRACTED FILTERS:
```json
{json.dumps(filters, indent=2)}
```

GENERATION RULES:
1. Create 2-6 sub-queries (more filters = more sub-queries)
2. Use synonym expansion for skills, roles, and domain terms
3. Combine multiple search strategies (skill arrays + job descriptions)
4. Assign priority: 1 (primary), 2 (secondary), 3 (optional)
5. Include clear rationale for each sub-query
6. Each sub-query must have: sub_query, tool, params, priority, rationale
7. Use valid tool names from the available tools list

EXECUTION STRATEGY:
- "parallel_intersect": Execute all priority 1 in parallel, then intersect results (for AND logic)
- "parallel_union": Execute all in parallel, then union results (for OR logic)
- "sequential": Execute in priority order, pass results between steps
- "hybrid": Mix of parallel and sequential based on dependencies

FEW-SHOT EXAMPLES:

Example 1 - Skill Search:
Filters: {{"skill_filters": ["Python"], "company_filters": [], ...}}
Output:
{{
  "original_query": "Find Python developers",
  "filters_used": {{"skill_filters": ["Python"]}},
  "sub_queries": [
    {{
      "sub_query": "Find people with Python in skill arrays",
      "tool": "find_people_by_skill",
      "params": {{"skill": "Python"}},
      "priority": 1,
      "rationale": "Direct match in technical_skills, secondary_skills, domain_knowledge arrays"
    }},
    {{
      "sub_query": "Find people with Python development experience in job descriptions",
      "tool": "search_job_descriptions_by_keywords",
      "params": {{"keywords": ["Python", "Python developer", "Python engineer", "Python programming"], "match_type": "any"}},
      "priority": 1,
      "rationale": "Contextual search with synonym expansion in job history"
    }},
    {{
      "sub_query": "Find people with Python technical expertise in job descriptions",
      "tool": "find_technical_skills_in_descriptions",
      "params": {{"tech_keywords": ["Python", "Django", "Flask", "FastAPI", "PyTorch"]}},
      "priority": 2,
      "rationale": "Deep technical search including related Python frameworks"
    }}
  ],
  "execution_strategy": "parallel_union",
  "total_sub_queries": 3
}}

Example 2 - Compound Search (Skill + Company):
Filters: {{"skill_filters": ["AI"], "company_filters": ["Google"], ...}}
Output:
{{
  "original_query": "AI experts at Google",
  "filters_used": {{"skill_filters": ["AI"], "company_filters": ["Google"]}},
  "sub_queries": [
    {{
      "sub_query": "Find people with AI/ML in skill arrays",
      "tool": "find_people_with_multiple_skills",
      "params": {{"skills_list": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning"], "match_type": "any"}},
      "priority": 1,
      "rationale": "Multi-skill search with AI synonyms"
    }},
    {{
      "sub_query": "Find people with AI experience in job descriptions",
      "tool": "search_job_descriptions_by_keywords",
      "params": {{"keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Neural Networks", "NLP"], "match_type": "any"}},
      "priority": 1,
      "rationale": "Contextual AI expertise search with expanded terms"
    }},
    {{
      "sub_query": "Find Google employees",
      "tool": "find_people_by_company",
      "params": {{"company_name": "Google"}},
      "priority": 1,
      "rationale": "Direct company match for intersection"
    }}
  ],
  "execution_strategy": "parallel_intersect",
  "total_sub_queries": 3
}}

Example 3 - Role-based Search:
Filters: {{"skill_filters": [], "other_criteria": {{"role": "founder"}}, ...}}
Output:
{{
  "original_query": "Find founders",
  "filters_used": {{"other_criteria": {{"role": "founder"}}}},
  "sub_queries": [
    {{
      "sub_query": "Find people with leadership indicators",
      "tool": "find_leadership_indicators",
      "params": {{}},
      "priority": 1,
      "rationale": "Identify leadership experience from job descriptions"
    }},
    {{
      "sub_query": "Find people with founder/entrepreneur keywords",
      "tool": "search_job_descriptions_by_keywords",
      "params": {{"keywords": ["founder", "co-founder", "CEO", "entrepreneur", "startup", "founded"], "match_type": "any"}},
      "priority": 1,
      "rationale": "Direct founder keyword search with variations"
    }}
  ],
  "execution_strategy": "parallel_union",
  "total_sub_queries": 2
}}

NOW GENERATE SUB-QUERIES FOR THESE FILTERS.
Return ONLY valid JSON matching the structure shown in examples."""

        return prompt
    
    def _validate_and_normalize(
        self,
        result: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and normalize the generation result."""
        
        # Ensure required fields
        normalized = {
            "original_query": result.get("original_query", filters.get("original_query", "")),
            "filters_used": result.get("filters_used", filters),
            "sub_queries": result.get("sub_queries", []),
            "execution_strategy": result.get("execution_strategy", "parallel_union"),
            "total_sub_queries": len(result.get("sub_queries", []))
        }
        
        # Validate each sub-query
        validated_sub_queries = []
        for sq in normalized["sub_queries"]:
            if not isinstance(sq, dict):
                continue
            
            # Check required fields
            if "tool" not in sq or "params" not in sq:
                continue
            
            # Validate tool name
            tool_name = sq.get("tool", "")
            if self.available_tools and tool_name not in self.available_tools:
                # Skip invalid tools
                continue
            
            validated_sq = {
                "sub_query": sq.get("sub_query", ""),
                "tool": tool_name,
                "params": sq.get("params", {}),
                "priority": sq.get("priority", 1),
                "rationale": sq.get("rationale", "")
            }
            validated_sub_queries.append(validated_sq)
        
        normalized["sub_queries"] = validated_sub_queries
        normalized["total_sub_queries"] = len(validated_sub_queries)
        
        return normalized
    
    def _empty_result(self, filters: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Return empty result with error information."""
        return {
            "original_query": filters.get("original_query", ""),
            "filters_used": filters,
            "sub_queries": [],
            "execution_strategy": "none",
            "total_sub_queries": 0,
            "meta": {
                "model": "fallback",
                "error": reason
            }
        }
    
    def get_sub_query_summary(self, result: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of generated sub-queries.
        
        Args:
            result: Output from generate()
            
        Returns:
            Human-readable summary string
        """
        sub_queries = result.get("sub_queries", [])
        if not sub_queries:
            return "No sub-queries generated"
        
        summary_parts = []
        summary_parts.append(f"Strategy: {result.get('execution_strategy', 'unknown')}")
        summary_parts.append(f"Total: {result.get('total_sub_queries', 0)} sub-queries")
        
        priority_groups = {}
        for sq in sub_queries:
            priority = sq.get("priority", 1)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(f"{sq.get('tool', 'unknown')} ({sq.get('sub_query', '')[:50]}...)")
        
        for priority in sorted(priority_groups.keys()):
            summary_parts.append(f"\nPriority {priority}:")
            for sq_desc in priority_groups[priority]:
                summary_parts.append(f"  - {sq_desc}")
        
        return "\n".join(summary_parts)


# Convenience function for testing
def generate_subqueries(filters: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick generation function for testing.
    
    Args:
        filters: Filters dict from QueryDecomposer
        api_key: Optional API key override
        
    Returns:
        Sub-queries result dict
    """
    generator = SubQueryGenerator(api_key=api_key)
    return generator.generate(filters)


# Main test block
if __name__ == "__main__":
    import sys
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("="*70)
        print("❌ ERROR: OPENAI_API_KEY not found")
        print("="*70)
        print("\nPlease ensure your .env file contains OPENAI_API_KEY")
        print("="*70)
        sys.exit(1)
    
    print("="*70)
    print("INTEGRATED PIPELINE TEST - Query Decomposer → SubQuery Generator")
    print("="*70)
    print("\nThis test shows the complete pipeline:")
    print("1. User Query → Query Decomposer → Filters")
    print("2. Filters → SubQuery Generator → Sub-queries with Tool Mappings")
    print("="*70)
    
    # Test queries (natural language)
    test_queries = [
        "Find Python developers at Google",
        "AI experts in Bangalore with 5+ years experience",
        "Find startup founders"
    ]
    
    # Check if QueryDecomposer is available
    if QueryDecomposer is None:
        print("\n❌ ERROR: QueryDecomposer not available")
        print("Cannot run integrated pipeline test")
        print("Run this file from the project root: python agent/nodes/planner/subquery_generator.py")
        sys.exit(1)
    
    # Initialize both components
    decomposer = QueryDecomposer()
    generator = SubQueryGenerator()
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"🔍 USER QUERY: {query}")
        print(f"{'='*70}")
        
        # STEP 1: Decompose query into filters
        print("\n📋 STEP 1: Query Decomposer")
        print("-" * 70)
        filters = decomposer.decompose(query)
        
        # Show decomposed filters
        filter_summary = decomposer.get_filter_summary(filters)
        print(f"Extracted Filters: {filter_summary}")
        print(f"Tokens Used: {filters.get('meta', {}).get('tokens_used', 0)}")
        
        # STEP 2: Generate sub-queries from filters
        print("\n📊 STEP 2: SubQuery Generator")
        print("-" * 70)
        result = generator.generate(filters)
        
        # Show generated sub-queries
        print(f"Execution Strategy: {result.get('execution_strategy', 'unknown')}")
        print(f"Total Sub-Queries: {result.get('total_sub_queries', 0)}")
        print(f"Tokens Used: {result.get('meta', {}).get('tokens_used', 0)}")
        
        # Show each sub-query
        for i, sq in enumerate(result.get('sub_queries', []), 1):
            print(f"\n  Sub-Query {i} (Priority {sq.get('priority', 1)}):")
            print(f"    Tool: {sq.get('tool', 'unknown')}")
            print(f"    Description: {sq.get('sub_query', '')[:80]}...")
            print(f"    Params: {json.dumps(sq.get('params', {}), indent=6)}")
        
        # Show complete output in JSON
        print("\n" + "="*70)
        print("� COMPLETE PIPELINE OUTPUT (JSON)")
        print("="*70)
        print(json.dumps(result, indent=2))
        print("="*70)
