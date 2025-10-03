# --- mcp/schemas/tool_schemas.py ---
from typing import Dict, Any, List

# Graph schema definition (from existing natural_language_search.py)
GRAPH_SCHEMA = """
Node properties are the following:
Person {id: INTEGER, name: STRING, linkedin_profile: STRING, email: STRING, phone: STRING, location: STRING, headline: STRING, summary: STRING, followers_count: FLOAT, total_experience_months: FLOAT},
Company {url: STRING, name: STRING},
Institution {url: STRING, name: STRING},
Skill {name: STRING} -- NOTE: Skill names are stored in lowercase

Relationship properties are the following:
WORKS_AT {title: STRING, start_date: STRING, end_date: STRING, duration_months: FLOAT, description: STRING, location: STRING},
STUDIED_AT {degree: STRING, start_year: INTEGER, end_year: INTEGER}

The relationships are the following:
(:Person)-[:WORKS_AT]->(:Company),
(:Person)-[:STUDIED_AT]->(:Institution),
(:Person)-[:HAS_SKILL]->(:Skill)

IMPORTANT: When searching for skills, always use lowercase for skill names.
Examples:
- For "Machine Learning" skills: MATCH (p:Person)-[:HAS_SKILL]->(s:Skill {name: 'machine learning'})
- For "Python" skills: MATCH (p:Person)-[:HAS_SKILL]->(s:Skill {name: 'python'})
"""

# MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "find_person_by_name",
        "description": "Find a specific person by their name (case-insensitive partial matching)",
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
        "description": "Find all people who have a specific skill (e.g., Python, machine learning, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": "The skill to search for (will be converted to lowercase automatically)"
                }
            },
            "required": ["skill"]
        }
    },
    {
        "name": "find_people_by_company",
        "description": "Find all people who have worked at a specific company",
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
        "name": "natural_language_search",
        "description": "Perform a natural language search across the knowledge graph using AI",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural language question to search the knowledge graph (e.g., 'Who has Python skills?', 'Who worked at Google?')"
                }
            },
            "required": ["question"]
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
        "description": "Get all skills for a specific person",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_name": {
                    "type": "string",
                    "description": "The name of the person to get skills for"
                }
            },
            "required": ["person_name"]
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
                "person_name": {
                    "type": "string",
                    "description": "The name of the person to find colleagues for"
                }
            },
            "required": ["person_name"]
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
        "name": "get_skill_popularity",
        "description": "Get the most popular skills by counting how many people have each skill",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of skills to return"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_person_details",
        "description": "Get comprehensive details about a person including skills, companies, and education",
        "inputSchema": {
            "type": "object",
            "properties": {
                "person_name": {
                    "type": "string",
                    "description": "The name of the person to get details for"
                }
            },
            "required": ["person_name"]
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