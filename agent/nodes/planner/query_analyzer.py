"""
Query Analyzer using GPT-5 Mini to intelligently select tools from the catalog.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from .tool_catalog import TOOL_CATALOG, get_all_tool_names


class QueryAnalyzer:
    """Analyzes user queries and selects appropriate tools using GPT-5 Mini."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-5-mini"
    ):
        """
        Initialize the QueryAnalyzer.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-5-mini)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.tool_catalog = TOOL_CATALOG
        self.available_tool_names = get_all_tool_names()
    
    def _create_analysis_prompt(self, query: str) -> str:
        """Create the analysis prompt with tool catalog and examples."""
        
        # Build compact tool reference
        tool_descriptions = []
        for tool in self.tool_catalog:
            params = ", ".join(tool.get("parameters", [])) or "none"
            use_when = tool.get("use_when", [""])[0]
            tool_descriptions.append(
                f"• {tool['name']} ({tool['category']})\n"
                f"  Params: {params}\n"
                f"  Use: {use_when}"
            )
        
        tools_text = "\n".join(tool_descriptions)
        
        prompt = f"""You are an expert query analyzer that selects appropriate tools from a catalog to answer queries about a professional network database.

AVAILABLE TOOLS:
{tools_text}

IMPORTANT RULES:
1. NEVER select "natural_language_search" - it is explicitly forbidden
2. Only use tools from the catalog above (19 tools total)
3. For skill searches, use "find_people_by_skill"
4. For company searches, use "find_people_by_company"
5. For institution searches, use "find_people_by_institution"
6. For location searches, use "find_people_by_location"
7. For combined criteria (e.g., "Python developers at Google"), select multiple tools and use "parallel_then_intersect" strategy
8. For profile details, use "find_person_by_name" first, then "get_person_details" or "get_person_complete_profile"
9. For person-specific queries with person_id/person_name parameters, you may need to call find_person_by_name first

FEW-SHOT EXAMPLES:

Example 1 - Simple skill search:
Query: "Find Python developers"
Response:
{{
  "breakdown": {{
    "original_query": "Find Python developers",
    "complexity": "simple",
    "intent": "skill_search",
    "entities": {{"skills": ["Python"], "companies": [], "locations": [], "institutions": []}}
  }},
  "tools_to_call": [
    {{"tool": "find_people_by_skill", "params": {{"skill": "Python"}}, "reason": "Direct skill match"}}
  ],
  "execution_strategy": "single_tool",
  "reasoning": "Simple skill search requires only find_people_by_skill"
}}

Example 2 - Compound search:
Query: "Python developers at Google"
Response:
{{
  "breakdown": {{
    "original_query": "Python developers at Google",
    "complexity": "compound",
    "intent": "skill_company_search",
    "entities": {{"skills": ["Python"], "companies": ["Google"], "locations": [], "institutions": []}}
  }},
  "tools_to_call": [
    {{"tool": "find_people_by_skill", "params": {{"skill": "Python"}}, "reason": "Find Python skill holders"}},
    {{"tool": "find_people_by_company", "params": {{"company_name": "Google"}}, "reason": "Find Google employees"}}
  ],
  "execution_strategy": "parallel_then_intersect",
  "reasoning": "Two criteria (skill AND company) require parallel execution then intersection"
}}

Example 3 - Profile lookup:
Query: "Show me details of John Smith"
Response:
{{
  "breakdown": {{
    "original_query": "Show me details of John Smith",
    "complexity": "simple",
    "intent": "profile_lookup",
    "entities": {{"names": ["John Smith"], "skills": [], "companies": [], "locations": [], "institutions": []}}
  }},
  "tools_to_call": [
    {{"tool": "find_person_by_name", "params": {{"name": "John Smith"}}, "reason": "Find person and get person_id"}},
    {{"tool": "get_person_details", "params": {{"person_name": "John Smith"}}, "reason": "Get comprehensive details"}}
  ],
  "execution_strategy": "sequential",
  "reasoning": "First find the person, then get their details"
}}

Example 4 - Job description search:
Query: "Who worked on microservices?"
Response:
{{
  "breakdown": {{
    "original_query": "Who worked on microservices?",
    "complexity": "simple",
    "intent": "job_description_search",
    "entities": {{"keywords": ["microservices"], "skills": [], "companies": [], "locations": []}}
  }},
  "tools_to_call": [
    {{"tool": "search_job_descriptions_by_keywords", "params": {{"keywords": ["microservices"], "match_type": "any"}}, "reason": "Search job descriptions for contextual mentions"}}
  ],
  "execution_strategy": "single_tool",
  "reasoning": "Job description keyword search for experience"
}}

NOW ANALYZE THIS QUERY:
User Query: "{query}"

Return ONLY valid JSON matching the structure shown in examples. No markdown, no explanations outside the JSON."""

        return prompt
    
    def analyze_query(
        self,
        query: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Analyze a user query and return tool selection plan.
        
        Args:
            query: User's natural language query
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with 'breakdown', 'tools_to_call', 'execution_strategy', 'reasoning'
        """
        if not query or not query.strip():
            return {
                "error": "Empty query",
                "breakdown": None,
                "tools_to_call": [],
                "execution_strategy": "none",
                "reasoning": "No query provided"
            }
        
        prompt = self._create_analysis_prompt(query)
        
        for attempt in range(max_retries + 1):
            try:
                # Use Chat Completions API for GPT-5 Mini
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert query analyzer. You always return valid JSON following the exact structure provided in examples. Never use natural_language_search tool."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_completion_tokens=1200  # GPT-5 uses max_completion_tokens
                )
                
                # Extract response text
                content = response.choices[0].message.content.strip()
                
                # Parse JSON from response
                result = self._parse_json_response(content)
                
                # Validate the result
                validation = self._validate_result(result, query)
                if validation["valid"]:
                    # Add metadata
                    result["meta"] = {
                        "model": self.model,
                        "attempt": attempt + 1,
                        "query": query
                    }
                    return result
                else:
                    if attempt < max_retries:
                        # Try again
                        continue
                    else:
                        # Return fallback on final attempt
                        return self._fallback_analysis(query, validation.get("error", "Validation failed"))
                    
            except Exception as e:
                if attempt < max_retries:
                    continue
                return self._fallback_analysis(query, f"Error: {str(e)}")
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from model response, handling markdown code blocks."""
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            # Extract content between ``` markers
            lines = content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]  # Remove first ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove last ```
            content = "\n".join(lines).strip()
        
        # Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
        
        raise ValueError(f"Could not parse JSON from response: {content[:200]}")
    
    def _validate_result(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validate the analysis result."""
        
        # Check required fields
        required_fields = ["breakdown", "tools_to_call", "execution_strategy", "reasoning"]
        for field in required_fields:
            if field not in result:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Validate tools
        tools = result.get("tools_to_call", [])
        if not isinstance(tools, list):
            return {"valid": False, "error": "tools_to_call must be a list"}
        
        for tool_entry in tools:
            if not isinstance(tool_entry, dict):
                return {"valid": False, "error": "Each tool entry must be a dict"}
            
            tool_name = tool_entry.get("tool", "")
            
            # Check if tool is in catalog
            if tool_name not in self.available_tool_names:
                return {"valid": False, "error": f"Invalid tool: {tool_name}"}
            
            # CRITICAL: Reject natural_language_search
            if tool_name == "natural_language_search":
                return {
                    "valid": False,
                    "error": "natural_language_search is forbidden - must use specific tools"
                }
        
        return {"valid": True}
    
    def _fallback_analysis(self, query: str, error_msg: str) -> Dict[str, Any]:
        """
        Provide a fallback analysis when LLM fails.
        Uses simple heuristics to select tools.
        """
        query_lower = query.lower()
        tools = []
        entities = {
            "skills": [],
            "companies": [],
            "locations": [],
            "institutions": [],
            "names": []
        }
        
        # Extract entities using simple patterns
        # Skills (common programming languages and technologies)
        skills = ["python", "java", "javascript", "react", "node", "sql", "aws", "machine learning", "ai"]
        for skill in skills:
            if skill in query_lower:
                entities["skills"].append(skill.title())
                tools.append({
                    "tool": "find_people_by_skill",
                    "params": {"skill": skill.title()},
                    "reason": f"Query mentions {skill}"
                })
        
        # Companies (common tech companies)
        companies = ["google", "microsoft", "amazon", "apple", "meta", "facebook", "netflix", "uber"]
        for company in companies:
            if company in query_lower:
                company_name = company.title()
                if company == "meta" or company == "facebook":
                    company_name = "Meta"
                entities["companies"].append(company_name)
                tools.append({
                    "tool": "find_people_by_company",
                    "params": {"company_name": company_name},
                    "reason": f"Query mentions {company_name}"
                })
        
        # Profile lookup patterns
        if any(word in query_lower for word in ["profile", "details", "show me", "who is"]):
            # Try to extract name (very simple)
            words = query.split()
            if len(words) >= 2:
                # Assume last two words might be a name
                potential_name = " ".join(words[-2:])
                entities["names"].append(potential_name)
                tools.append({
                    "tool": "get_profile_by_name",
                    "params": {"name": potential_name},
                    "reason": "Profile lookup query"
                })
        
        # Aggregation patterns
        if any(word in query_lower for word in ["most common", "popular", "top", "aggregate"]):
            if "skill" in query_lower:
                tools.append({
                    "tool": "aggregate_skills",
                    "params": {},
                    "reason": "Aggregation query for skills"
                })
            elif "company" in query_lower or "companies" in query_lower:
                tools.append({
                    "tool": "aggregate_companies",
                    "params": {},
                    "reason": "Aggregation query for companies"
                })
        
        # If no tools found, use a generic search tool
        if not tools:
            # Pick most generic tool based on query type
            if any(word in query_lower for word in ["find", "search", "people", "who"]):
                tools.append({
                    "tool": "find_people_by_skill",
                    "params": {"skill": "programming"},
                    "reason": "Generic search fallback"
                })
        
        execution_strategy = "parallel_then_intersect" if len(tools) > 1 else "single_tool"
        
        return {
            "breakdown": {
                "original_query": query,
                "complexity": "simple" if len(tools) <= 1 else "compound",
                "intent": "search",
                "entities": entities
            },
            "tools_to_call": tools,
            "execution_strategy": execution_strategy,
            "reasoning": f"Fallback analysis due to: {error_msg}",
            "meta": {
                "model": "fallback_heuristic",
                "error": error_msg
            }
        }


# Convenience function for quick testing
def analyze_query(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick analysis function for testing.
    
    Args:
        query: User query string
        api_key: Optional API key override
        
    Returns:
        Analysis result dict
    """
    analyzer = QueryAnalyzer(api_key=api_key)
    return analyzer.analyze_query(query)


if __name__ == "__main__":
    # Simple test
    import sys
    
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    else:
        test_query = "Find Python developers at Google"
    
    print(f"Analyzing: {test_query}")
    print("-" * 50)
    
    result = analyze_query(test_query)
    print(json.dumps(result, indent=2))
