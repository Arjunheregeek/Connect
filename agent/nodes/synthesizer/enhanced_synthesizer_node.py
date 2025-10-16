"""
Enhanced Synthesizer Node for LangGraph Agent

This node takes the person IDs extracted by the executor and:
1. Fetches complete profiles for top N candidates via MCP
2. Ranks/scores them based on relevance to the original query
3. Generates a natural language response using GPT-4o
4. Formats the response in a human-readable way

Input from state:
    - accumulated_data: List[int] (person IDs from executor)
    - user_query: str (original natural language query)
    - filters: Dict (extracted filters from planner)
    - tool_results: List[Dict] (tool execution results)

Output to state:
    - response: str (natural language formatted response)
    - synthesizer_metadata: Dict (token usage, profiles fetched, etc.)
    - workflow_status: str (updated to 'complete')
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Try to import from agent.state with fallback
try:
    from agent.state.types import AgentState
except ImportError:
    # Fallback for standalone execution
    from typing import TypedDict
    class AgentState(TypedDict, total=False):
        user_query: str
        filters: Dict[str, Any]
        sub_queries: List[Dict[str, Any]]
        execution_strategy: str
        planning_metadata: Dict[str, Any]
        tool_results: List[Dict[str, Any]]
        accumulated_data: List[Any]
        response: str
        synthesizer_metadata: Dict[str, Any]
        workflow_status: str
        errors: List[str]

# Try to import MCP client
try:
    from agent.mcp_client.mcp_client import MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  MCP Client not available")


async def enhanced_synthesizer_node(state: AgentState) -> AgentState:
    """
    Enhanced Synthesizer node that converts person IDs to natural language response.
    
    Synthesis Flow:
    1. Read person IDs from state (from enhanced_executor_node)
    2. Fetch complete profiles for top N candidates (default: 10)
    3. Score/rank candidates based on relevance
    4. Generate natural language response using GPT-4o
    5. Format response with proper sections and details
    6. Store response in state
    
    State Input (from executor):
        - accumulated_data: List[int] (person IDs)
        - user_query: str (original query)
        - filters: Dict (extracted filters)
        - tool_results: List[Dict] (tool execution details)
    
    State Output (to user):
        - response: str (formatted natural language response)
        - synthesizer_metadata: Dict (synthesis details)
        - workflow_status: str ('complete')
    
    Args:
        state: Current AgentState with person IDs
        
    Returns:
        Updated AgentState with natural language response
    """
    
    # Update status
    state['workflow_status'] = 'synthesizing'
    
    # Check if MCP client is available
    if not MCP_AVAILABLE or not MCPClient:
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append("MCP Client not available for synthesis")
        state['workflow_status'] = 'error'
        state['final_response'] = "Error: Unable to fetch person profiles."
        return state
    
    try:
        person_ids = state.get('accumulated_data', [])
        user_query = state.get('user_query', '')
        filters = state.get('filters', {})
        tool_results = state.get('tool_results', [])
        
        if not person_ids:
            state['final_response'] = "I couldn't find any people matching your search criteria. Please try refining your query."
            state['workflow_status'] = 'complete'
            state['synthesizer_metadata'] = {
                'total_person_ids': 0,
                'profiles_fetched': 0,
                'token_usage': 0
            }
            return state
        
        print(f"\n{'='*70}")
        print(f"ENHANCED SYNTHESIZER NODE - PROFILE SYNTHESIS")
        print(f"{'='*70}")
        print(f"📊 Total person IDs: {len(person_ids)}")
        print(f"🎯 Original query: {user_query}")
        
        # Step 1: Determine how many profiles we want
        desired_count = state.get('desired_count', 5)  # Default to 5 profiles
        top_n = min(len(person_ids), desired_count)
        
        # Step 2: Check if we already have complete profile data from tool_results
        # If get_person_complete_profile was called, we can reuse that data
        profiles = []
        profiles_from_cache = extract_profiles_from_tool_results(tool_results)
        
        if profiles_from_cache:
            print(f"✅ Using {len(profiles_from_cache)} cached profiles from tool_results")
            profiles = profiles_from_cache
        else:
            # Step 3: Fetch complete profiles via MCP
            print(f"📥 Fetching top {top_n} profiles (desired: {desired_count}, available: {len(person_ids)})...")
            profiles = await fetch_person_profiles(person_ids[:top_n])
            print(f"✅ Successfully fetched {len(profiles)} complete profiles")
        
        # Step 3: Generate natural language response
        response, token_usage = generate_natural_language_response(
            profiles=profiles,
            user_query=user_query,
            total_matches=len(person_ids),
            filters=filters
        )
        
        # Step 4: Update state
        state['final_response'] = response  # Changed from 'response' to 'final_response'
        state['profiles'] = profiles  # NEW: Store raw profiles for frontend
        state['synthesizer_metadata'] = {
            'total_person_ids': len(person_ids),
            'profiles_fetched': len(profiles),
            'token_usage': token_usage,
            'top_n': top_n
        }
        state['workflow_status'] = 'complete'
        
        print(f"\n✅ Synthesis Complete:")
        print(f"   - Total matches: {len(person_ids)}")
        print(f"   - Profiles fetched: {len(profiles)}")
        print(f"   - GPT-4o tokens used: {token_usage}")
        print(f"   - Response length: {len(response)} characters")
        print(f"{'='*70}\n")
        
        return state
        
    except Exception as e:
        print(f"\n❌ Error in synthesizer node: {e}")
        import traceback
        traceback.print_exc()
        
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Synthesizer error: {str(e)}")
        state['workflow_status'] = 'error'
        state['final_response'] = f"Error generating response: {str(e)}"
        return state


async def fetch_person_profiles(person_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Fetch complete profiles for a list of person IDs via MCP.
    
    Args:
        person_ids: List of person IDs to fetch
        
    Returns:
        List of complete person profile dictionaries
    """
    profiles = []
    
    async with MCPClient(base_url="http://localhost:8000") as mcp_client:
        # Fetch profiles in parallel for speed
        tasks = [
            mcp_client.tools.get_person_complete_profile(person_id=pid)
            for pid in person_ids
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"  ⚠️  Error fetching profile for person_id {person_ids[i]}: {response}")
                continue
            
            if response.success and response.data:
                # Parse the MCP response
                profile_data = parse_profile_response(response.data)
                if profile_data:
                    profiles.append(profile_data)
    
    return profiles


def extract_profiles_from_tool_results(tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract complete profile data from cached tool_results.
    
    If get_person_complete_profile was already called, we can reuse that data
    instead of re-fetching from MCP.
    
    Args:
        tool_results: List of tool execution results from executor
        
    Returns:
        List of complete person profile dictionaries
    """
    profiles = []
    
    for result in tool_results:
        # Only process successful get_person_complete_profile calls
        if not result.get('success'):
            continue
            
        tool_name = result.get('tool_name', '')
        if tool_name != 'get_person_complete_profile':
            continue
        
        # Extract profile from response_data
        response_data = result.get('response_data')
        if not response_data:
            continue
        
        profile_data = parse_profile_response(response_data)
        if profile_data:
            profiles.append(profile_data)
    
    return profiles


def parse_profile_response(response_data: Any) -> Dict[str, Any]:
    """
    Parse MCP response to extract profile data.
    
    MCP returns: {content: [{type: "text", text: "[{...}]"}]}
    We need to extract and parse the stringified data.
    """
    try:
        import json
        import ast
        
        if not isinstance(response_data, dict):
            return None
        
        # Extract stringified data from MCP response
        content = response_data.get('content', [])
        if not content:
            return None
        
        text_content = content[0].get('text', '') if isinstance(content, list) and len(content) > 0 else ''
        if not text_content:
            return None
        
        # Parse stringified data - try multiple parsing strategies
        try:
            # Strategy 1: Direct JSON parsing
            parsed_data = json.loads(text_content)
        except (json.JSONDecodeError, ValueError):
            try:
                # Strategy 2: Preprocess for Neo4j DateTime, nan, and HTML entities, then ast.literal_eval
                import re
                import html
                
                # Decode HTML entities (&amp; -> &)
                text_processed = html.unescape(text_content)
                
                # Replace Neo4j DateTime objects with string representation
                # Pattern: neo4j.time.DateTime(2025, 10, 9, 12, 8, 29, 8740000)
                text_processed = re.sub(
                    r'neo4j\.time\.DateTime\([^)]+\)',
                    'None',
                    text_processed
                )
                
                # Also handle other potential Neo4j types
                text_processed = re.sub(r'neo4j\.[a-zA-Z.]+\([^)]+\)', 'None', text_processed)
                
                # Handle nan (floating point NaN)
                text_processed = re.sub(r'\bnan\b', 'None', text_processed)
                
                # Clean up whitespace
                text_processed = text_processed.replace('\n', ' ').replace('\r', '')
                
                parsed_data = ast.literal_eval(text_processed)
            except (ValueError, SyntaxError) as e:
                print(f"  ⚠️  ast.literal_eval failed: {str(e)[:100]}")
                try:
                    # Strategy 3: Replace single quotes with double quotes and try JSON again
                    import re
                    import html
                    
                    text_cleaned = html.unescape(text_content)
                    # Remove Neo4j objects first
                    text_cleaned = re.sub(r'neo4j\.[a-zA-Z.]+\([^)]+\)', 'null', text_cleaned)
                    # Handle nan
                    text_cleaned = re.sub(r'\bnan\b', 'null', text_cleaned)
                    text_cleaned = text_cleaned.replace("'", '"')
                    # Handle None, True, False (Python) -> null, true, false (JSON)
                    text_cleaned = re.sub(r'\bNone\b', 'null', text_cleaned)
                    text_cleaned = re.sub(r'\bTrue\b', 'true', text_cleaned)
                    text_cleaned = re.sub(r'\bFalse\b', 'false', text_cleaned)
                    parsed_data = json.loads(text_cleaned)
                except (json.JSONDecodeError, ValueError) as e2:
                    print(f"  ⚠️  JSON parsing also failed: {str(e2)[:100]}")
                    return None
        
        # Extract first profile if it's a list
        if isinstance(parsed_data, list) and len(parsed_data) > 0:
            return parsed_data[0]
        elif isinstance(parsed_data, dict):
            return parsed_data
        
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error parsing profile response: {e}")
        return None


def generate_natural_language_response(
    profiles: List[Dict[str, Any]],
    user_query: str,
    total_matches: int,
    filters: Dict[str, Any]
) -> tuple[str, int]:
    """
    Generate natural language response using GPT-4o.
    
    Args:
        profiles: List of complete person profiles
        user_query: Original user query
        total_matches: Total number of matches found
        filters: Extracted filters from query
        
    Returns:
        Tuple of (response_text, token_usage)
    """
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Prepare profile summaries for GPT-4o
    profile_summaries = []
    for profile in profiles:
        summary = format_profile_summary(profile)
        profile_summaries.append(summary)
    
    # Create prompt for GPT-4o
    prompt = f"""You are a professional recruiter presenting candidate profiles to a hiring manager.

Original Search Query: "{user_query}"

Search Results Summary:
- Total matches found: {total_matches}
- Top profiles shown: {len(profiles)}

Extracted Search Criteria:
{format_filters(filters)}

Candidate Profiles:
{chr(10).join(profile_summaries)}

Your Task:
Generate a professional, human-readable response that:
1. Starts with a brief summary of the search results
2. IMPORTANT: Present EVERY SINGLE candidate profile provided below - do not skip any profiles
3. For each candidate, use this EXACT format (DO NOT use markdown bold ** or italic _ anywhere):

#### N. [Candidate Name]
Current Role: [Title] at [Company]
Location: [Location]
Key Skills: [Comma-separated list]
Relevant Experience:
  - [Experience highlight 1]
  - [Experience highlight 2]
Contact Information:
  - LinkedIn: [URL]
  - Email: [Email if available]
Why a Good Match: [Brief explanation]

4. Uses numbered sections (####) for each candidate
5. Maintains a professional yet friendly tone
6. CRITICAL: NO BOLD (**), NO ITALIC (_), NO MARKDOWN FORMATTING - use plain text only
7. All field names (Current Role, Location, Key Skills, etc.) should be plain text, not bold

CRITICAL: You must include ALL {len(profiles)} candidates in your response. Do not summarize or skip any profiles.

Format the response in a clear, structured way that a hiring manager can easily scan and understand.
Use PLAIN TEXT ONLY - no ** or _ characters for formatting.
"""
    
    # Call GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a professional recruiter who presents candidate profiles in a clear, structured, and engaging way."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=4000  # Increased to accommodate more profiles (approx 250 tokens per profile)
    )
    
    response_text = response.choices[0].message.content
    token_usage = response.usage.total_tokens
    
    return response_text, token_usage


def format_profile_summary(profile: Dict[str, Any]) -> str:
    """
    Format a single profile into a structured summary for GPT-4o.
    """
    # Handle total_experience_months safely (could be None)
    total_exp_months = profile.get('total_experience_months') or 0
    if isinstance(total_exp_months, (int, float)) and total_exp_months > 0:
        years = int(total_exp_months) // 12
        months = int(total_exp_months) % 12
        experience_str = f"{years} years {months} months"
    else:
        experience_str = "N/A"
    
    lines = [
        f"\n{'='*60}",
        f"Profile ID: {profile.get('person_id', 'N/A')}",
        f"Name: {profile.get('name', 'N/A')}",
        f"Headline: {profile.get('headline', 'N/A')}",
        f"Current Role: {profile.get('current_title', 'N/A')} at {profile.get('current_company', 'N/A')}",
        f"Location: {profile.get('location', 'N/A')}",
        f"Total Experience: {experience_str}",
        ""
    ]
    
    # Skills
    technical_skills = profile.get('technical_skills', [])
    if technical_skills:
        lines.append(f"Technical Skills: {', '.join(technical_skills[:10])}")
    
    secondary_skills = profile.get('secondary_skills', [])
    if secondary_skills:
        lines.append(f"Secondary Skills: {', '.join(secondary_skills[:10])}")
    
    domain_knowledge = profile.get('domain_knowledge', [])
    if domain_knowledge:
        lines.append(f"Domain Knowledge: {', '.join(domain_knowledge[:5])}")
    
    lines.append("")
    
    # Summary
    summary = profile.get('summary', '')
    if summary:
        lines.append(f"Summary: {summary[:300]}..." if len(summary) > 300 else f"Summary: {summary}")
        lines.append("")
    
    # Work History (top 2 recent roles)
    work_history = profile.get('work_history', [])
    if work_history:
        lines.append("Recent Work History:")
        for i, job in enumerate(work_history[:2]):
            lines.append(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            if job.get('description'):
                desc = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
                lines.append(f"     {desc}")
        lines.append("")
    
    # Contact
    email = profile.get('email', '')
    linkedin = profile.get('linkedin_profile', '')
    if email or linkedin:
        lines.append("Contact Information:")
        if email:
            lines.append(f"  Email: {email}")
        if linkedin:
            lines.append(f"  LinkedIn: {linkedin}")
    
    lines.append(f"{'='*60}\n")
    
    return '\n'.join(lines)


def format_filters(filters: Dict[str, Any]) -> str:
    """
    Format extracted filters into readable text.
    """
    lines = []
    
    for key, value in filters.items():
        if value:
            # Convert key from snake_case to Title Case
            display_key = key.replace('_', ' ').title()
            
            if isinstance(value, list):
                lines.append(f"- {display_key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"- {display_key}: {value}")
    
    return '\n'.join(lines) if lines else "No specific filters extracted"


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ENHANCED SYNTHESIZER NODE - STANDALONE TEST")
    print("="*70)
    print("\nNote: This requires MCP server to be running on port 8000")
    print("="*70)
    
    # Create test state with sample data
    test_state: AgentState = {
        'user_query': "Find Python developers with Machine Learning skills at IIT Bombay",
        'accumulated_data': [
            332592352,  # Sample person IDs
            420177476,
            102380764
        ],
        'filters': {
            'technical_skills': ['Python', 'Machine Learning'],
            'institution_filters': ['IIT Bombay'],
            'location_filters': []
        },
        'tool_results': [
            {
                'tool_name': 'find_people_by_technical_skill',
                'success': True,
                'person_count': 35
            },
            {
                'tool_name': 'find_people_by_institution',
                'success': True,
                'person_count': 50
            }
        ],
        'workflow_status': 'tools_complete'
    }
    
    # Run synthesizer
    result_state = asyncio.run(enhanced_synthesizer_node(test_state))
    
    # Display results
    print("\n" + "="*70)
    print("SYNTHESIS RESULTS")
    print("="*70)
    print(f"\nWorkflow Status: {result_state.get('workflow_status')}")
    print(f"\nMetadata:")
    metadata = result_state.get('synthesizer_metadata', {})
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    print(f"\n{'='*70}")
    print("GENERATED RESPONSE:")
    print(f"{'='*70}")
    print(result_state.get('response', 'No response generated'))
    print(f"{'='*70}")
