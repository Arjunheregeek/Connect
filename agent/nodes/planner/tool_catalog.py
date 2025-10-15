"""
Tool Catalog for Query Analyzer

Provides structured metadata about the 14 actual MCP tools (13 query tools + health_check)
to help the query analyzer select appropriate tools based on user queries.

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
    # CORE PERSON PROFILE TOOLS (10 tools)
    # =================================================================
    {
        "name": "get_person_complete_profile",
        "category": "person_profile",
        "description": "Get complete profile for a person including 12 essential properties and work history with job descriptions. Returns person_id, name, headline, linkedin_profile, location, current_company, current_title, total_experience_months, technical_skills, secondary_skills, domain_knowledge, and work_history.",
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
        "name": "find_people_by_technical_skill",
        "category": "person_profile",
        "description": "Find people by technical skills ONLY - searches technical_skills array (Python, AWS, ML, Kubernetes, SQL, etc.). Use this for programming languages, frameworks, tools, and technical abilities.",
        "parameters": ["skill"],
        "use_when": [
            "User asks for technical skills or programming languages",
            "Query mentions frameworks, tools, technologies",
            "Need to find developers/engineers with specific technical expertise"
        ],
        "keywords": ["Python", "Java", "JavaScript", "AWS", "Kubernetes", "Docker", "SQL", "React", "ML", "AI", "technical", "programming", "framework", "tool", "technology", "developer", "engineer"],
        "example_queries": [
            "Find Python developers",
            "Who knows AWS?",
            "Engineers with Kubernetes experience",
            "People skilled in machine learning"
        ]
    },
    {
        "name": "find_people_by_secondary_skill",
        "category": "person_profile",
        "description": "Find people by secondary/soft skills ONLY - searches secondary_skills array (Leadership, Communication, Project Management, etc.). Use this for soft skills, leadership abilities, and non-technical skills.",
        "parameters": ["skill"],
        "use_when": [
            "User asks for soft skills or leadership abilities",
            "Query mentions communication, management, strategic skills",
            "Need to find people with non-technical expertise"
        ],
        "keywords": ["leadership", "communication", "management", "strategic", "soft skills", "interpersonal", "collaboration", "negotiation", "presentation", "mentoring", "coaching"],
        "example_queries": [
            "Find leaders",
            "Who has strong communication skills?",
            "People with project management experience",
            "Engineers with mentoring skills"
        ]
    },
    {
        "name": "find_people_by_current_company",
        "category": "person_profile",
        "description": "Find CURRENT employees of a specific company - fast property-based search using current_company field. Use this when you need only people who currently work at a company.",
        "parameters": ["company_name"],
        "use_when": [
            "User asks for current employees only",
            "Query uses 'currently works at', 'now at', 'present'",
            "Need fast lookup of active employees"
        ],
        "keywords": ["currently works at", "current employees", "now at", "works at now", "present at", "currently at", "active employees"],
        "example_queries": [
            "Who currently works at Google?",
            "Current Microsoft employees",
            "People now working at Amazon",
            "Active employees at Apple"
        ]
    },
    {
        "name": "find_people_by_company_history",
        "category": "person_profile",
        "description": "Find ALL people who have worked at a specific company (current AND past employees). Uses CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT relationships. Use this for company alumni searches or when you need both current and past employees.",
        "parameters": ["company_name"],
        "use_when": [
            "User asks about people who have EVER worked at a company",
            "Need both current and past employees",
            "Query asks for 'worked at' (past tense) or 'alumni'",
            "Company history or alumni search"
        ],
        "keywords": ["worked at", "has worked at", "company", "employer", "employees", "alumni", "former employees", "past and present", "ever worked"],
        "example_queries": [
            "Who has worked at Google?",
            "Find all people from Microsoft (past and present)",
            "Google alumni",
            "Anyone who worked at Amazon"
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
    
    # =================================================================
    # JOB DESCRIPTION ANALYSIS TOOLS (3 tools)
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
