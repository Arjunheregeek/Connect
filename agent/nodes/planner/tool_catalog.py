"""
Tool Catalog for Query Analyzer

Provides structured metadata about 23 specific MCP tools to help the query analyzer
select appropriate tools based on user queries.

NOTE: natural_language_search is intentionally excluded - we want precise tool selection.
"""

from typing import List, Dict, Any

TOOL_CATALOG = [
    # =================================================================
    # CORE SEARCH TOOLS (14 tools) - excludes natural_language_search
    # =================================================================
    {
        "name": "find_person_by_name",
        "category": "core_search",
        "description": "Find a specific person by their name (case-insensitive partial matching)",
        "parameters": ["name"],
        "use_when": [
            "User mentions a specific person's name",
            "Query asks about a particular individual",
            "Need to identify a person before other operations"
        ],
        "keywords": ["find", "who is", "person", "named", "name", "called"],
        "example_queries": [
            "Find John Smith",
            "Who is Sarah Chen?",
            "Tell me about Mike Johnson"
        ]
    },
    {
        "name": "find_people_by_skill",
        "category": "core_search",
        "description": "Find all people who have a specific skill",
        "parameters": ["skill"],
        "use_when": [
            "User asks for people with a specific technical skill",
            "Query mentions programming languages, technologies, or skills",
            "Need to find experts in a particular area"
        ],
        "keywords": ["skill", "developer", "engineer", "programmer", "expert", "knows", "has experience with"],
        "example_queries": [
            "Find Python developers",
            "Who knows machine learning?",
            "People with React skills"
        ]
    },
    {
        "name": "find_people_by_company",
        "category": "core_search",
        "description": "Find all people who have worked at a specific company",
        "parameters": ["company_name"],
        "use_when": [
            "User asks about people at a specific company",
            "Query mentions a company name",
            "Need to find current or former employees"
        ],
        "keywords": ["works at", "worked at", "company", "employer", "employees", "at Google", "from Microsoft"],
        "example_queries": [
            "Who works at Google?",
            "Find people from Microsoft",
            "Employees at Amazon"
        ]
    },
    {
        "name": "find_people_by_institution",
        "category": "core_search",
        "description": "Find all people who studied at a specific institution or university",
        "parameters": ["institution_name"],
        "use_when": [
            "User asks about people from a specific university",
            "Query mentions educational institution",
            "Need to find alumni"
        ],
        "keywords": ["studied at", "graduated from", "university", "college", "institution", "alumni", "school"],
        "example_queries": [
            "People from Stanford",
            "Who studied at MIT?",
            "Stanford graduates"
        ]
    },
    {
        "name": "find_people_by_location",
        "category": "core_search",
        "description": "Find all people in a specific location or city",
        "parameters": ["location"],
        "use_when": [
            "User asks for people in a specific city or location",
            "Geographic filtering is needed",
            "Query mentions a location"
        ],
        "keywords": ["in", "located in", "from", "living in", "based in", "location", "city"],
        "example_queries": [
            "Engineers in San Francisco",
            "People from New York",
            "Who lives in Seattle?"
        ]
    },
    {
        "name": "find_people_with_multiple_skills",
        "category": "core_search",
        "description": "Find people who have multiple specific skills with AND/OR logic",
        "parameters": ["skills_list", "match_type"],
        "use_when": [
            "User asks for people with multiple skills",
            "Query uses 'and' or 'or' between skills",
            "Need combination of skills"
        ],
        "keywords": ["and", "or", "both", "multiple skills", "combination"],
        "example_queries": [
            "Python and JavaScript developers",
            "People with React or Vue",
            "Engineers with both ML and Python"
        ]
    },
    {
        "name": "get_person_skills",
        "category": "core_search",
        "description": "Get all skills for a specific person",
        "parameters": ["person_name"],
        "use_when": [
            "User asks what skills a person has",
            "Need to list someone's expertise",
            "Query asks about person's capabilities"
        ],
        "keywords": ["skills", "what can", "expertise", "knows", "proficient in"],
        "example_queries": [
            "What skills does John have?",
            "Show me Sarah's expertise",
            "List Mike's skills"
        ]
    },
    {
        "name": "get_person_details",
        "category": "core_search",
        "description": "Get comprehensive details about a person including skills, companies, and education",
        "parameters": ["person_name"],
        "use_when": [
            "User asks for full information about a person",
            "Need complete profile",
            "Query asks to 'tell me about' someone"
        ],
        "keywords": ["details", "about", "profile", "information", "tell me about", "who is"],
        "example_queries": [
            "Tell me about John Smith",
            "Show me Sarah's profile",
            "Get details for Mike"
        ]
    },
    {
        "name": "get_person_colleagues",
        "category": "core_search",
        "description": "Get all colleagues of a person across all companies they worked at",
        "parameters": ["person_name"],
        "use_when": [
            "User asks about someone's colleagues",
            "Need to find people who worked with someone",
            "Query asks about connections or coworkers"
        ],
        "keywords": ["colleagues", "coworkers", "worked with", "connections", "teammates"],
        "example_queries": [
            "Who are John's colleagues?",
            "Find Sarah's coworkers",
            "People who worked with Mike"
        ]
    },
    {
        "name": "find_colleagues_at_company",
        "category": "core_search",
        "description": "Find colleagues of a specific person at a given company",
        "parameters": ["person_id", "company_name"],
        "use_when": [
            "User asks about colleagues at a specific company",
            "Need to find people who worked together at one place",
            "Query specifies both person and company"
        ],
        "keywords": ["colleagues at", "worked with at", "teammates at", "coworkers at"],
        "example_queries": [
            "Who worked with John at Google?",
            "Sarah's colleagues at Microsoft",
            "Find Mike's teammates at Amazon"
        ]
    },
    {
        "name": "find_people_by_experience_level",
        "category": "core_search",
        "description": "Find people based on their total work experience in months",
        "parameters": ["min_months", "max_months"],
        "use_when": [
            "User asks for people with specific experience range",
            "Query mentions years/months of experience",
            "Need to filter by seniority"
        ],
        "keywords": ["experience", "years", "senior", "junior", "experienced", "5+ years"],
        "example_queries": [
            "Developers with 5+ years experience",
            "Senior engineers",
            "People with 2-3 years experience"
        ]
    },
    {
        "name": "get_company_employees",
        "category": "core_search",
        "description": "Get all employees (past and present) of a specific company",
        "parameters": ["company_name"],
        "use_when": [
            "User asks for all employees of a company",
            "Need complete list of company workers",
            "Query asks 'who works/worked at'"
        ],
        "keywords": ["all employees", "everyone at", "all people at", "workforce"],
        "example_queries": [
            "All employees at Google",
            "Everyone who worked at Microsoft",
            "Get all Amazon employees"
        ]
    },
    {
        "name": "get_skill_popularity",
        "category": "core_search",
        "description": "Get the most popular skills by counting how many people have each skill",
        "parameters": ["limit"],
        "use_when": [
            "User asks about most common skills",
            "Need statistics on skills",
            "Query asks 'what are popular skills'"
        ],
        "keywords": ["popular skills", "most common", "top skills", "skill statistics"],
        "example_queries": [
            "What are the most popular skills?",
            "Show me top 10 skills",
            "Most common technologies"
        ]
    },
    # NOTE: natural_language_search tool is intentionally excluded
    # We want specific, targeted tool selection rather than broad AI search
    {
        "name": "health_check",
        "category": "core_search",
        "description": "Check the health status of the knowledge graph database and services",
        "parameters": [],
        "use_when": [
            "User asks about system status",
            "Query mentions health or status",
            "Debugging purposes"
        ],
        "keywords": ["health", "status", "working", "available", "online"],
        "example_queries": [
            "Is the system working?",
            "Check health",
            "System status"
        ]
    },
    
    # =================================================================
    # JOB DESCRIPTION ANALYSIS TOOLS (9 tools)
    # =================================================================
    {
        "name": "get_person_job_descriptions",
        "category": "job_analysis",
        "description": "Get all job descriptions for a person with company and role details",
        "parameters": ["person_name"],
        "use_when": [
            "User asks about someone's work history",
            "Need detailed job descriptions",
            "Query asks about roles or responsibilities"
        ],
        "keywords": ["job description", "work history", "roles", "responsibilities", "what did", "work experience"],
        "example_queries": [
            "What did John do at Google?",
            "Show me Sarah's work history",
            "Get Mike's job descriptions"
        ]
    },
    {
        "name": "search_job_descriptions_by_keywords",
        "category": "job_analysis",
        "description": "Search for people based on keywords in their job descriptions",
        "parameters": ["keywords", "match_type"],
        "use_when": [
            "User searches for experience with specific keywords",
            "Need to find contextual mentions in job descriptions",
            "Query asks about specific experience or responsibilities"
        ],
        "keywords": ["experience with", "worked on", "responsible for", "managed", "developed"],
        "example_queries": [
            "Who worked on microservices?",
            "Find people who managed teams",
            "Experience with cloud infrastructure"
        ]
    },
    {
        "name": "find_technical_skills_in_descriptions",
        "category": "job_analysis",
        "description": "Find people who mention specific technical skills in their job descriptions",
        "parameters": ["tech_keywords"],
        "use_when": [
            "User looks for specific technical mentions",
            "Need to find contextual technical expertise",
            "Query asks about technologies used in work"
        ],
        "keywords": ["used", "worked with", "implemented", "built with", "technology"],
        "example_queries": [
            "Who used Kubernetes in their work?",
            "Find people who built with React",
            "Engineers who worked with AWS"
        ]
    },
    {
        "name": "find_leadership_indicators",
        "category": "job_analysis",
        "description": "Find people with leadership indicators in their job descriptions",
        "parameters": [],
        "use_when": [
            "User asks for leaders or managers",
            "Need to identify leadership experience",
            "Query mentions management or leadership"
        ],
        "keywords": ["leader", "manager", "lead", "director", "head of", "managed team"],
        "example_queries": [
            "Find engineering managers",
            "Who has leadership experience?",
            "People who led teams"
        ]
    },
    {
        "name": "find_achievement_patterns",
        "category": "job_analysis",
        "description": "Find people with quantifiable achievements in their job descriptions",
        "parameters": [],
        "use_when": [
            "User asks for high achievers",
            "Need to find people with measurable impact",
            "Query mentions achievements or results"
        ],
        "keywords": ["achieved", "improved", "increased", "reduced", "metrics", "results", "impact"],
        "example_queries": [
            "Find high performers",
            "Who has measurable achievements?",
            "People with proven results"
        ]
    },
    {
        "name": "analyze_career_progression",
        "category": "job_analysis",
        "description": "Analyze a person's career progression by examining job titles and descriptions over time",
        "parameters": ["person_name"],
        "use_when": [
            "User asks about career growth",
            "Need to understand career trajectory",
            "Query asks how someone progressed"
        ],
        "keywords": ["career progression", "career path", "growth", "advancement", "trajectory"],
        "example_queries": [
            "How did John's career progress?",
            "Show me Sarah's career growth",
            "Analyze Mike's career path"
        ]
    },
    {
        "name": "find_domain_experts",
        "category": "job_analysis",
        "description": "Find people with deep domain expertise based on job description analysis",
        "parameters": ["domain_keywords"],
        "use_when": [
            "User asks for domain experts",
            "Need to find specialists in a field",
            "Query mentions specific domain or industry"
        ],
        "keywords": ["expert in", "specialist", "domain", "industry", "fintech", "healthcare", "e-commerce"],
        "example_queries": [
            "Find fintech experts",
            "Who specializes in healthcare?",
            "E-commerce domain experts"
        ]
    },
    {
        "name": "find_similar_career_paths",
        "category": "job_analysis",
        "description": "Find people with similar career paths to a reference person",
        "parameters": ["reference_person_name", "similarity_threshold"],
        "use_when": [
            "User asks for people with similar backgrounds",
            "Need to find comparable career trajectories",
            "Query asks 'who is similar to'"
        ],
        "keywords": ["similar to", "like", "comparable", "same path", "similar background"],
        "example_queries": [
            "Find people similar to John",
            "Who has a career like Sarah's?",
            "Similar backgrounds to Mike"
        ]
    },
    {
        "name": "find_role_transition_patterns",
        "category": "job_analysis",
        "description": "Find people who transitioned from one type of role to another",
        "parameters": ["from_role_keywords", "to_role_keywords"],
        "use_when": [
            "User asks about career transitions",
            "Need to find people who switched roles",
            "Query mentions career pivots or changes"
        ],
        "keywords": ["transitioned", "moved from", "switched", "pivot", "changed from"],
        "example_queries": [
            "Who moved from engineering to management?",
            "Find people who transitioned to leadership",
            "Engineers who became product managers"
        ]
    }
]


def get_tool_by_name(tool_name: str) -> Dict[str, Any]:
    """Get a specific tool from the catalog by name"""
    for tool in TOOL_CATALOG:
        if tool["name"] == tool_name:
            return tool
    return None


def get_tools_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all tools in a specific category"""
    return [tool for tool in TOOL_CATALOG if tool["category"] == category]


def get_all_tool_names() -> List[str]:
    """Get list of all tool names"""
    return [tool["name"] for tool in TOOL_CATALOG]


def search_tools_by_keywords(keywords: List[str]) -> List[Dict[str, Any]]:
    """Find tools that match any of the given keywords"""
    matching_tools = []
    keywords_lower = [k.lower() for k in keywords]
    
    for tool in TOOL_CATALOG:
        tool_keywords = [k.lower() for k in tool["keywords"]]
        if any(kw in tool_keywords for kw in keywords_lower):
            matching_tools.append(tool)
    
    return matching_tools
