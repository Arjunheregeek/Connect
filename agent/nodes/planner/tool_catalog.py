"""
Tool Catalog for Query Analyzer

Provides structured metadata about the 19 actual MCP tools to help the query analyzer
select appropriate tools based on user queries.

IMPORTANT: This catalog reflects the ACTUAL tools available in the system.
All parameters and descriptions match the real Neo4j schema and query implementations.
"""

from typing import List, Dict, Any

TOOL_CATALOG = [
    # =================================================================
    # SYSTEM TOOLS (1 tool)
    # =================================================================
    {
        "name": "health_check",
        "category": "system",
        "description": "Check the health status of the Neo4j knowledge graph database and MCP services",
        "parameters": [],
        "use_when": [
            "User asks about system status",
            "Query mentions health, status, or availability",
            "Debugging or troubleshooting"
        ],
        "keywords": ["health", "status", "working", "available", "online", "check"],
        "example_queries": [
            "Is the system working?",
            "Check health",
            "System status"
        ]
    },
    
    # =================================================================
    # CORE PERSON PROFILE TOOLS (13 tools)
    # =================================================================
    {
        "name": "get_person_complete_profile",
        "category": "person_profile",
        "description": "Get complete profile for a person including ALL 35 properties, work history with job descriptions, and education. This is the heavyweight query that returns everything.",
        "parameters": ["person_id", "person_name"],
        "optional_params": ["person_id", "person_name"],
        "use_when": [
            "User asks for complete information about a person",
            "Need ALL details including work history and education",
            "Query asks for full profile or comprehensive data"
        ],
        "keywords": ["complete", "full profile", "everything", "all details", "comprehensive"],
        "example_queries": [
            "Give me everything about John Smith",
            "Full profile for Sarah Chen",
            "Complete information on Mike Johnson"
        ]
    },
    {
        "name": "find_person_by_name",
        "category": "person_profile",
        "description": "Find a person by their name (case-insensitive partial matching). Returns lightweight profile with person_id.",
        "parameters": ["name"],
        "use_when": [
            "User mentions a specific person's name",
            "Need to identify a person and get their person_id",
            "First step before other operations requiring person_id"
        ],
        "keywords": ["find", "who is", "person", "named", "name", "called", "search for"],
        "example_queries": [
            "Find John Smith",
            "Who is Sarah Chen?",
            "Search for Mike Johnson"
        ]
    },
    {
        "name": "find_people_by_skill",
        "category": "person_profile",
        "description": "Find all people who have a specific skill. Searches across technical_skills, secondary_skills, and domain_knowledge arrays on Person nodes.",
        "parameters": ["skill"],
        "use_when": [
            "User asks for people with a specific skill",
            "Query mentions programming languages, technologies, or expertise",
            "Need to find experts in a particular area"
        ],
        "keywords": ["skill", "developer", "engineer", "programmer", "expert", "knows", "has experience with", "proficient in"],
        "example_queries": [
            "Find Python developers",
            "Who knows machine learning?",
            "People with React skills"
        ]
    },
    {
        "name": "find_people_by_company",
        "category": "person_profile",
        "description": "Find all people who worked at a specific company (current or past). Uses CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT relationships.",
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
        "name": "find_colleagues_at_company",
        "category": "person_profile",
        "description": "Find colleagues of a specific person at a given company. Requires person_id (get from find_person_by_name first).",
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
        "name": "find_people_by_institution",
        "category": "person_profile",
        "description": "Find all people who studied at a specific institution or university. Uses STUDIED_AT relationships.",
        "parameters": ["institution_name"],
        "use_when": [
            "User asks about people from a specific university or institution",
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
        "category": "person_profile",
        "description": "Find all people in a specific location or city. Searches current_location property on Person nodes.",
        "parameters": ["location"],
        "use_when": [
            "User asks for people in a specific city or location",
            "Geographic filtering is needed",
            "Query mentions a location or city"
        ],
        "keywords": ["in", "located in", "from", "living in", "based in", "location", "city"],
        "example_queries": [
            "Engineers in San Francisco",
            "People from New York",
            "Who lives in Seattle?"
        ]
    },
    {
        "name": "get_person_skills",
        "category": "person_profile",
        "description": "Get all skills for a specific person from their skill arrays (technical_skills, secondary_skills, domain_knowledge).",
        "parameters": ["person_id", "person_name"],
        "optional_params": ["person_id", "person_name"],
        "use_when": [
            "User asks what skills a person has",
            "Need to list someone's expertise",
            "Query asks about person's capabilities or knowledge"
        ],
        "keywords": ["skills", "what can", "expertise", "knows", "proficient in", "capabilities"],
        "example_queries": [
            "What skills does John have?",
            "Show me Sarah's expertise",
            "List Mike's skills"
        ]
    },
    {
        "name": "find_people_with_multiple_skills",
        "category": "person_profile",
        "description": "Find people who have multiple specific skills with AND/OR logic. match_type can be 'any' (OR) or 'all' (AND).",
        "parameters": ["skills_list", "match_type"],
        "use_when": [
            "User asks for people with multiple skills",
            "Query uses 'and' or 'or' between skills",
            "Need combination of skills"
        ],
        "keywords": ["and", "or", "both", "multiple skills", "combination", "all of"],
        "example_queries": [
            "Python and JavaScript developers",
            "People with React or Vue",
            "Engineers with both ML and Python"
        ]
    },
    {
        "name": "get_person_colleagues",
        "category": "person_profile",
        "description": "Get all colleagues of a person across all companies they worked at. Uses CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT relationships.",
        "parameters": ["person_id", "person_name"],
        "optional_params": ["person_id", "person_name"],
        "use_when": [
            "User asks about someone's colleagues",
            "Need to find people who worked with someone",
            "Query asks about connections or coworkers"
        ],
        "keywords": ["colleagues", "coworkers", "worked with", "connections", "teammates", "network"],
        "example_queries": [
            "Who are John's colleagues?",
            "Find Sarah's coworkers",
            "People who worked with Mike"
        ]
    },
    {
        "name": "find_people_by_experience_level",
        "category": "person_profile",
        "description": "Find people based on their total work experience in months. Uses total_experience_months property.",
        "parameters": ["min_months", "max_months"],
        "optional_params": ["min_months", "max_months"],
        "use_when": [
            "User asks for people with specific experience range",
            "Query mentions years/months of experience",
            "Need to filter by seniority or experience level"
        ],
        "keywords": ["experience", "years", "months", "senior", "junior", "experienced", "5+ years"],
        "example_queries": [
            "Developers with 5+ years experience",
            "Senior engineers",
            "People with 2-3 years experience"
        ]
    },
    {
        "name": "get_company_employees",
        "category": "person_profile",
        "description": "Get all employees (past and present) of a specific company. Uses CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT relationships.",
        "parameters": ["company_name"],
        "use_when": [
            "User asks for all employees of a company",
            "Need complete list of company workers",
            "Query asks 'who works/worked at' or 'all employees'"
        ],
        "keywords": ["all employees", "everyone at", "all people at", "workforce", "team at"],
        "example_queries": [
            "All employees at Google",
            "Everyone who worked at Microsoft",
            "Get all Amazon employees"
        ]
    },
    {
        "name": "get_person_details",
        "category": "person_profile",
        "description": "Get comprehensive details about a person including skills, companies, and education - summary view (lighter than get_person_complete_profile).",
        "parameters": ["person_id", "person_name"],
        "optional_params": ["person_id", "person_name"],
        "use_when": [
            "User asks for details about a person",
            "Need summary information (not full profile)",
            "Query asks 'tell me about' or 'details on'"
        ],
        "keywords": ["details", "about", "information", "tell me about", "summary"],
        "example_queries": [
            "Tell me about John Smith",
            "Details on Sarah Chen",
            "Information about Mike"
        ]
    },
    
    # =================================================================
    # JOB DESCRIPTION ANALYSIS TOOLS (5 tools)
    # =================================================================
    {
        "name": "get_person_job_descriptions",
        "category": "job_analysis",
        "description": "Get all job descriptions for a person with company and role details. Accesses description property on work relationships.",
        "parameters": ["person_id", "person_name"],
        "optional_params": ["person_id", "person_name"],
        "use_when": [
            "User asks about someone's work history",
            "Need detailed job descriptions",
            "Query asks about roles, responsibilities, or what someone did"
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
        "description": "Search for people based on keywords in their job descriptions. match_type can be 'any' (OR) or 'all' (AND).",
        "parameters": ["keywords", "match_type"],
        "use_when": [
            "User searches for experience with specific keywords",
            "Need to find contextual mentions in job descriptions",
            "Query asks about specific experience, responsibilities, or achievements"
        ],
        "keywords": ["experience with", "worked on", "responsible for", "managed", "developed", "built"],
        "example_queries": [
            "Who worked on microservices?",
            "Find people who managed teams",
            "Experience with cloud infrastructure"
        ]
    },
    {
        "name": "find_technical_skills_in_descriptions",
        "category": "job_analysis",
        "description": "Find people who mention specific technical skills in their job descriptions. Goes beyond structured skill arrays to find contextual mentions.",
        "parameters": ["tech_keywords"],
        "use_when": [
            "User looks for specific technical mentions",
            "Need to find contextual technical expertise",
            "Query asks about technologies used in actual work"
        ],
        "keywords": ["used", "worked with", "implemented", "built with", "technology", "technical"],
        "example_queries": [
            "Who used Kubernetes in their work?",
            "Find people who built with React",
            "Engineers who worked with AWS"
        ]
    },
    {
        "name": "find_leadership_indicators",
        "category": "job_analysis",
        "description": "Find people with leadership indicators in their job descriptions. Looks for management, team lead, and leadership-related keywords.",
        "parameters": [],
        "use_when": [
            "User asks for leaders or managers",
            "Need to identify leadership experience",
            "Query mentions management, leadership, or team lead"
        ],
        "keywords": ["leader", "manager", "lead", "director", "head of", "managed team", "leadership"],
        "example_queries": [
            "Find engineering managers",
            "Who has leadership experience?",
            "People who led teams"
        ]
    },
    {
        "name": "find_domain_experts",
        "category": "job_analysis",
        "description": "Find people with deep domain expertise based on job description analysis. Requires at least 2 jobs in the domain.",
        "parameters": ["domain_keywords"],
        "use_when": [
            "User asks for domain experts",
            "Need to find specialists in a field",
            "Query mentions specific domain, industry, or vertical"
        ],
        "keywords": ["expert in", "specialist", "domain", "industry", "fintech", "healthcare", "e-commerce"],
        "example_queries": [
            "Find fintech experts",
            "Who specializes in healthcare?",
            "E-commerce domain experts"
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
