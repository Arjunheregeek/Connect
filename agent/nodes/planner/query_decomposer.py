"""
Query Decomposer - Step 1 of Enhanced Query Processing

Extracts structured filters from natural language queries using LLM.
This is the first step before generating sub-queries and tool calls.

Workflow:
1. User Query + Graph Schema → LLM → Structured Filters
2. Filters → SubQueryGenerator (next file)
"""

import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Import graph schema from MCP schemas
try:
    from mcp.schemas.tool_schemas import GRAPH_SCHEMA
except ImportError:
    # Fallback schema if import fails
    GRAPH_SCHEMA = """
    Person nodes with properties: skills, company, location, experience, etc.
    Company nodes, Institution nodes
    Relationships: WORKS_AT, STUDIED_AT
    """


class QueryDecomposer:
    """
    Decomposes natural language queries into structured filters.
    
    Example:
        Input: "Find AI experts at Adobe in Bangalore with 5+ years experience"
        Output: {
            "skill_filters": ["AI", "Machine Learning"],
            "company_filters": ["Adobe"],
            "location_filters": ["Bangalore"],
            "experience_filters": {"min_years": 5},
            "seniority_filters": [],
            "name_filters": [],
            "institution_filters": []
        }
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize Query Decomposer.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-4o - GPT-4 Optimized)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.graph_schema = GRAPH_SCHEMA
    
    def decompose(
        self,
        query: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Decompose a natural language query into structured filters.
        
        Args:
            query: User's natural language query
            max_retries: Maximum retry attempts if parsing fails
            
        Returns:
            Dictionary with extracted filters:
            {
                "original_query": str,
                "skill_filters": List[str],
                "company_filters": List[str],
                "location_filters": List[str],
                "experience_filters": Dict[str, Any],
                "seniority_filters": List[str],
                "name_filters": List[str],
                "institution_filters": List[str],
                "other_criteria": Dict[str, Any]
            }
        """
        if not query or not query.strip():
            return self._empty_filters(query, "Empty query provided")
        
        prompt = self._create_decomposition_prompt(query)
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at extracting structured information from natural language queries about professional networks. Always return valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},  # Force JSON output
                    temperature=0.3,  # Low temperature for consistent extraction
                    max_tokens=800
                )
                
                content = response.choices[0].message.content.strip()
                result = json.loads(content)
                
                # Validate and normalize the result
                validated = self._validate_and_normalize(result, query)
                
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
                return self._empty_filters(query, f"Decomposition failed: {str(e)}")
    
    def _create_decomposition_prompt(self, query: str) -> str:
        """Create the LLM prompt for query decomposition."""
        
        prompt = f"""You are analyzing a query about a professional network database with the following schema:

{self.graph_schema}

Your task is to extract structured filters from the user's natural language query.

FILTER CATEGORIES:
1. skill_filters: Programming languages, technologies, technical skills (e.g., Python, AWS, Machine Learning)
2. company_filters: Company names where people work or worked (e.g., Google, Microsoft, Adobe)
3. location_filters: Cities, regions, or countries (e.g., San Francisco, India, California)
4. experience_filters: Years or months of experience (e.g., {{"min_years": 5, "max_years": 10}})
5. seniority_filters: Job levels (e.g., Senior, Junior, Lead, Manager, Director)
6. name_filters: Specific person names mentioned (e.g., John Smith, Sarah Chen)
7. institution_filters: Universities or educational institutions (e.g., MIT, Stanford, IIT Bombay)
8. other_criteria: Any other relevant criteria like industry, job title, availability, etc.

EXTRACTION RULES:
- Extract all mentions of skills/technologies as separate items
- Capture company names exactly as mentioned
- Extract location names (cities, states, countries)
- Parse experience requirements into min/max years or months
- Identify seniority levels from keywords like "senior", "junior", "lead"
- Extract person names if query is about specific individuals
- Identify educational institutions
- Put any other criteria in "other_criteria" as key-value pairs

FEW-SHOT EXAMPLES:

Example 1:
Query: "Find Python developers at Google"
Response:
{{
  "original_query": "Find Python developers at Google",
  "skill_filters": ["Python"],
  "company_filters": ["Google"],
  "location_filters": [],
  "experience_filters": {{}},
  "seniority_filters": [],
  "name_filters": [],
  "institution_filters": [],
  "other_criteria": {{}}
}}

Example 2:
Query: "AI experts in Bangalore with 5+ years experience"
Response:
{{
  "original_query": "AI experts in Bangalore with 5+ years experience",
  "skill_filters": ["AI", "Artificial Intelligence", "Machine Learning"],
  "company_filters": [],
  "location_filters": ["Bangalore"],
  "experience_filters": {{"min_years": 5}},
  "seniority_filters": [],
  "name_filters": [],
  "institution_filters": [],
  "other_criteria": {{}}
}}

Example 3:
Query: "Senior React developers at Microsoft or Amazon in Seattle"
Response:
{{
  "original_query": "Senior React developers at Microsoft or Amazon in Seattle",
  "skill_filters": ["React", "JavaScript"],
  "company_filters": ["Microsoft", "Amazon"],
  "location_filters": ["Seattle"],
  "experience_filters": {{}},
  "seniority_filters": ["Senior"],
  "name_filters": [],
  "institution_filters": [],
  "other_criteria": {{}}
}}

Example 4:
Query: "Tell me about John Smith's colleagues at Adobe"
Response:
{{
  "original_query": "Tell me about John Smith's colleagues at Adobe",
  "skill_filters": [],
  "company_filters": ["Adobe"],
  "location_filters": [],
  "experience_filters": {{}},
  "seniority_filters": [],
  "name_filters": ["John Smith"],
  "institution_filters": [],
  "other_criteria": {{"query_type": "colleagues"}}
}}

Example 5:
Query: "IIT Bombay graduates working in fintech"
Response:
{{
  "original_query": "IIT Bombay graduates working in fintech",
  "skill_filters": [],
  "company_filters": [],
  "location_filters": [],
  "experience_filters": {{}},
  "seniority_filters": [],
  "name_filters": [],
  "institution_filters": ["IIT Bombay", "Indian Institute of Technology Bombay"],
  "other_criteria": {{"industry": "fintech"}}
}}

NOW EXTRACT FILTERS FROM THIS QUERY:
User Query: "{query}"

Return ONLY valid JSON matching the structure shown in examples."""

        return prompt
    
    def _validate_and_normalize(
        self,
        result: Dict[str, Any],
        original_query: str
    ) -> Dict[str, Any]:
        """Validate and normalize the decomposition result."""
        
        # Ensure all required fields exist
        normalized = {
            "original_query": result.get("original_query", original_query),
            "skill_filters": result.get("skill_filters", []),
            "company_filters": result.get("company_filters", []),
            "location_filters": result.get("location_filters", []),
            "experience_filters": result.get("experience_filters", {}),
            "seniority_filters": result.get("seniority_filters", []),
            "name_filters": result.get("name_filters", []),
            "institution_filters": result.get("institution_filters", []),
            "other_criteria": result.get("other_criteria", {})
        }
        
        # Convert any non-list fields to lists (defensive programming)
        for key in ["skill_filters", "company_filters", "location_filters", 
                    "seniority_filters", "name_filters", "institution_filters"]:
            if not isinstance(normalized[key], list):
                normalized[key] = [normalized[key]] if normalized[key] else []
        
        # Ensure experience_filters is a dict
        if not isinstance(normalized["experience_filters"], dict):
            normalized["experience_filters"] = {}
        
        # Ensure other_criteria is a dict
        if not isinstance(normalized["other_criteria"], dict):
            normalized["other_criteria"] = {}
        
        return normalized
    
    def _empty_filters(self, query: str, reason: str) -> Dict[str, Any]:
        """Return empty filter structure with error information."""
        return {
            "original_query": query,
            "skill_filters": [],
            "company_filters": [],
            "location_filters": [],
            "experience_filters": {},
            "seniority_filters": [],
            "name_filters": [],
            "institution_filters": [],
            "other_criteria": {},
            "meta": {
                "model": "fallback",
                "error": reason
            }
        }
    
    def get_filter_summary(self, filters: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of extracted filters.
        
        Args:
            filters: Result from decompose()
            
        Returns:
            Human-readable summary string
        """
        parts = []
        
        if filters.get("skill_filters"):
            parts.append(f"Skills: {', '.join(filters['skill_filters'])}")
        
        if filters.get("company_filters"):
            parts.append(f"Companies: {', '.join(filters['company_filters'])}")
        
        if filters.get("location_filters"):
            parts.append(f"Locations: {', '.join(filters['location_filters'])}")
        
        if filters.get("experience_filters"):
            exp = filters["experience_filters"]
            exp_parts = []
            if "min_years" in exp:
                exp_parts.append(f"min {exp['min_years']} years")
            if "max_years" in exp:
                exp_parts.append(f"max {exp['max_years']} years")
            if exp_parts:
                parts.append(f"Experience: {', '.join(exp_parts)}")
        
        if filters.get("seniority_filters"):
            parts.append(f"Seniority: {', '.join(filters['seniority_filters'])}")
        
        if filters.get("name_filters"):
            parts.append(f"Names: {', '.join(filters['name_filters'])}")
        
        if filters.get("institution_filters"):
            parts.append(f"Institutions: {', '.join(filters['institution_filters'])}")
        
        if filters.get("other_criteria"):
            other = ", ".join(f"{k}={v}" for k, v in filters["other_criteria"].items())
            parts.append(f"Other: {other}")
        
        return " | ".join(parts) if parts else "No filters extracted"


# Convenience function for testing
def decompose_query(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick decomposition function for testing.
    
    Args:
        query: User query string
        api_key: Optional API key override
        
    Returns:
        Decomposition result dict
    """
    decomposer = QueryDecomposer(api_key=api_key)
    return decomposer.decompose(query)


# Main test block
if __name__ == "__main__":
    import sys
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("="*70)
        print("❌ ERROR: OPENAI_API_KEY not found")
        print("="*70)
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nThen run the test again:")
        print("  python agent/nodes/planner/query_decomposer.py")
        print("="*70)
        sys.exit(1)
    
    # Test queries
    test_queries = [
        "Find Python developers at Google",
        "AI experts in Bangalore with 5+ years experience",
        "Senior React developers at Microsoft or Amazon in Seattle",
        "Tell me about John Smith",
        "IIT Bombay graduates working in fintech"
    ]
    
    # Use command line argument or default tests
    if len(sys.argv) > 1:
        test_queries = [" ".join(sys.argv[1:])]
    
    print("="*70)
    print("QUERY DECOMPOSER - TEST MODE")
    print("="*70)
    
    decomposer = QueryDecomposer()
    
    for query in test_queries:
        print(f"\n📋 Query: {query}")
        print("-" * 70)
        
        result = decomposer.decompose(query)
        
        # Pretty print the result
        print(json.dumps(result, indent=2))
        
        # Print summary
        summary = decomposer.get_filter_summary(result)
        print(f"\n📊 Summary: {summary}")
        print("="*70)
