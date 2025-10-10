# --- mcp/schemas/tool_schemas.py ---
from typing import Dict, Any, List

# Graph schema definition - Based on actual Neo4j database structure from importer.py
GRAPH_SCHEMA = """
Node properties are the following:
Person {
    person_id: INTEGER (unique identifier),
    name: STRING,
    linkedin_profile: STRING,
    email: STRING,
    phone: STRING,
    current_location: STRING,
    headline: STRING,
    summary: STRING,
    followers_count: FLOAT,
    trustworthiness_score: INTEGER,
    perceived_expertise_level: INTEGER,
    competence_score: INTEGER,
    current_title: STRING,
    current_company: STRING,
    industry: STRING,
    seniority_level: STRING,
    years_of_experience: FLOAT,
    employment_type: STRING,
    professional_status: STRING,
    primary_expertise: STRING,
    total_experience_months: FLOAT,
    technical_skills: LIST<STRING>,
    secondary_skills: LIST<STRING>,
    domain_knowledge: LIST<STRING>,
    degrees: LIST<STRING>,
    current_goals: STRING,
    current_challenges: STRING,
    resources_needed: STRING,
    availability_hiring: STRING,
    availability_roles: STRING,
    availability_cofounder: STRING,
    availability_advisory: STRING,
    updated_at: DATETIME
},
Company {name: STRING (unique), created_at: DATETIME},
Institution {name: STRING (unique), created_at: DATETIME}

Relationship properties are the following:
CURRENTLY_WORKS_AT {role: STRING, start_date: STRING, end_date: STRING, duration_months: FLOAT, description: STRING, location: STRING, is_current: BOOLEAN, created_at: DATETIME},
PREVIOUSLY_WORKED_AT {role: STRING, start_date: STRING, end_date: STRING, duration_months: FLOAT, description: STRING, location: STRING, is_current: BOOLEAN, created_at: DATETIME},
STUDIED_AT {degree: STRING, start_year: INTEGER, end_year: INTEGER, created_at: DATETIME}

The relationships are the following:
(:Person)-[:CURRENTLY_WORKS_AT]->(:Company),
(:Person)-[:PREVIOUSLY_WORKED_AT]->(:Company),
(:Person)-[:STUDIED_AT]->(:Institution)

IMPORTANT NOTES:
- Skills are stored as ARRAYS directly on Person nodes (technical_skills, secondary_skills, domain_knowledge), NOT as separate Skill nodes
- Work relationships are SPLIT into CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT (not a single WORKS_AT relationship)
- The relationship property for job title is 'role', NOT 'title'
- Person identifier is 'person_id', NOT 'id'
- Person location is 'current_location', NOT 'location'
- Education dates use start_year/end_year (INTEGER), NOT start_date/end_date
"""

# MCP Tool Definitions - Based on actual QueryManager methods in src/query.py
MCP_TOOLS = [
    {
        "name": "get_person_complete_profile",
        "description": "Get complete profile for a person including ALL 35 properties, work history with job descriptions, and education history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "integer",
                    "description": "The unique person ID (preferred)"
                },
                "person_name": {
                    "type": "string",
                    "description": "The person's name (alternative identifier)"
                }
            },
            "required": []
        }
    },
    {
        "name": "find_person_by_name",
        "description": "Find a person by their name (case-insensitive partial matching) - returns lightweight profile with person_id",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the person to search for (partial names are supported)"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "find_people_by_skill",
        "description": "Find all people who have a specific skill - searches across technical_skills, secondary_skills, and domain_knowledge arrays",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": "The skill to search for (case-insensitive)"
                }
            },
            "required": ["skill"]
        }
    },
    {
        "name": "find_people_by_company",
        "description": "Find all people who have worked at a specific company (current or past)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The name of the company to search for (partial names are supported)"
                }
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "find_colleagues_at_company",
        "description": "Find colleagues of a specific person at a given company",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "integer",
                    "description": "The ID of the person to find colleagues for"
                },
                "company_name": {
                    "type": "string",
                    "description": "The name of the company where they worked together"
                }
            },
            "required": ["person_id", "company_name"]
        }
    },
    {
        "name": "find_people_by_institution",
        "description": "Find all people who studied at a specific institution or university",
        "inputSchema": {
            "type": "object",
            "properties": {
                "institution_name": {
                    "type": "string",
                    "description": "The name of the institution/university to search for"
                }
            },
            "required": ["institution_name"]
        }
    },
    {
        "name": "find_people_by_location",
        "description": "Find all people in a specific location or city",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location/city to search for"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_person_skills",
        "description": "Get all skills for a specific person from their skill arrays (technical_skills, secondary_skills, domain_knowledge)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "integer",
                    "description": "The person ID (preferred)"
                },
                "person_name": {
                    "type": "string",
                    "description": "The person name (alternative)"
                }
            },
            "required": []
        }
    },
    {
        "name": "find_people_with_multiple_skills",
        "description": "Find people who have multiple specific skills with AND/OR logic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skills_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of skills to search for"
                },
                "match_type": {
                    "type": "string",
                    "enum": ["any", "all"],
                    "default": "any",
                    "description": "Match 'any' skill (OR) or 'all' skills (AND)"
                }
            },
            "required": ["skills_list"]
        }
    },
    {
        "name": "get_person_colleagues",
        "description": "Get all colleagues of a person across all companies they worked at",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "integer",
                    "description": "The person ID (preferred)"
                },
                "person_name": {
                    "type": "string",
                    "description": "The person name (alternative)"
                }
            },
            "required": []
        }
    },
    {
        "name": "find_people_by_experience_level",
        "description": "Find people based on their total work experience in months",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_months": {
                    "type": "integer",
                    "description": "Minimum experience in months"
                },
                "max_months": {
                    "type": "integer",
                    "description": "Maximum experience in months"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_company_employees",
        "description": "Get all employees (past and present) of a specific company",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The name of the company to get employees for"
                }
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "get_person_details",
        "description": "Get comprehensive details about a person including skills, companies, and education - summary view",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "integer",
                    "description": "The person ID (preferred)"
                },
                "person_name": {
                    "type": "string",
                    "description": "The person name (alternative)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_person_job_descriptions",
        "description": "Get all job descriptions for a person with company and role details - foundation for technical skill discovery, behavioral analysis, and career progression",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "integer",
                    "description": "The person ID (preferred)"
                },
                "person_name": {
                    "type": "string",
                    "description": "The person name (alternative)"
                }
            },
            "required": []
        }
    },
    {
        "name": "search_job_descriptions_by_keywords",
        "description": "Search for people based on keywords in their job descriptions - useful for finding technical skills, behavioral patterns, or specific experience",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of keywords to search for in job descriptions"
                },
                "match_type": {
                    "type": "string",
                    "enum": ["any", "all"],
                    "default": "any",
                    "description": "Match 'any' keyword (OR) or 'all' keywords (AND)"
                }
            },
            "required": ["keywords"]
        }
    },
    {
        "name": "find_technical_skills_in_descriptions",
        "description": "Find people who mention specific technical skills in their job descriptions - goes beyond structured skills to find contextual technical mentions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tech_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of technical terms to search for (e.g., python, kubernetes, machine learning)"
                }
            },
            "required": ["tech_keywords"]
        }
    },
    {
        "name": "find_leadership_indicators",
        "description": "Find people with leadership indicators in their job descriptions - looks for management, team lead, and leadership-related keywords",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "find_domain_experts",
        "description": "Find people with deep domain expertise based on job description analysis - requires at least 2 jobs in the domain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domain-specific terms (e.g., fintech, healthcare, e-commerce)"
                }
            },
            "required": ["domain_keywords"]
        }
    },
    {
        "name": "health_check",
        "description": "Check the health status of the knowledge graph database and services",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def get_tool_by_name(tool_name: str) -> Dict[str, Any]:
    """Get a specific tool definition by name"""
    for tool in MCP_TOOLS:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"Tool '{tool_name}' not found")

def get_all_tool_names() -> List[str]:
    """Get a list of all available tool names"""
    return [tool["name"] for tool in MCP_TOOLS]

def validate_tool_input(tool_name: str, input_data: Dict[str, Any]) -> bool:
    """Validate input data against a tool's schema"""
    tool = get_tool_by_name(tool_name)
    required_fields = tool["inputSchema"].get("required", [])
    
    # Check required fields
    for field in required_fields:
        if field not in input_data:
            raise ValueError(f"Missing required field '{field}' for tool '{tool_name}'")
    
    return True
