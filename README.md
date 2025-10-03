# Connect: Professional Network Knowledge Graph & MCP Server

This repository provides a comprehensive professional network knowledge graph system with an advanced MCP (Model Context Protocol) server for LangGraph agents. The system transforms raw professional profile data into a structured Neo4j knowledge graph and provides intelligent analysis capabilities through 24 specialized tools.

## 🚀 Features

### **Knowledge Graph System**
- **1,992 Professional Profiles** stored in Neo4j database
- **Rich Job Description Data** with detailed work experience, skills, and career progression
- **Multi-dimensional Relationships** between people, companies, skills, and institutions
- **Optimized Graph Queries** for fast data retrieval and analysis

### **MCP Server for LangGraph Agents**
- **24 Specialized Tools** for comprehensive professional network analysis
- **9 Advanced Job Description Analysis Tools** for career insights
- **Production-Ready FastAPI Server** with authentication and security
- **Intelligent Caching System** with 50%+ average hit rate
- **Complete Input Validation** and error handling

## 🔧 Architecture

### **Data Pipeline**
The system transforms raw CSV data through multiple processing stages:
1. **Raw Data Extraction** - Parse complex JSON structures from LinkedIn-style profiles
2. **Data Cleaning & Structuring** - Extract key entities and relationships
3. **Graph Database Import** - Load structured data into Neo4j with optimized schema
4. **MCP Server Integration** - Expose data through standardized protocol for AI agents

## 🛠 Available Tools

### **Core Professional Network Tools (15)**
| Tool | Description |
|------|-------------|
| `find_person_by_name` | Find people by name with fuzzy matching |
| `get_person_details` | Get comprehensive profile information |
| `natural_language_search` | AI-powered semantic search across profiles |
| `find_people_by_skill` | Find professionals with specific skills |
| `find_people_by_company` | Search by current or past company |
| `get_person_skills` | Get all skills for a specific person |
| `find_colleagues_at_company` | Find colleagues at specific companies |
| `get_person_colleagues` | Get all colleagues across career history |
| `find_people_by_experience_level` | Filter by total experience in months |
| `get_company_employees` | Get all employees of a company |
| `find_people_by_institution` | Search by educational institution |
| `find_people_by_location` | Geographic-based search |
| `find_people_with_multiple_skills` | Advanced skill combination queries |
| `get_skill_popularity` | Get most common skills in network |
| `health_check` | Server health and database status |

### **🆕 Job Description Analysis Tools (9)**
| Tool | Description |
|------|-------------|
| `get_person_job_descriptions` | Detailed work history with job descriptions |
| `search_job_descriptions_by_keywords` | Search across all job descriptions |
| `find_technical_skills_in_descriptions` | Find people with specific technical skills |
| `find_leadership_indicators` | Identify leadership experience patterns |
| `find_achievement_patterns` | Find quantifiable achievements |
| `analyze_career_progression` | Analyze career trajectory and growth |
| `find_domain_experts` | Discover deep expertise in domains |
| `find_similar_career_paths` | Match similar career trajectories |
| `find_role_transition_patterns` | Analyze career transitions and pivots |

## 📊 Data Processing Pipeline

### **Raw Data Processing**
**Source:** `People for People Table v1 (1).csv` with complex nested JSON structures
**Output:** `Processed_People_Knowledge_Graph.csv` with structured, graph-ready data

**Key Extraction Steps:**
- **Core Identity Attributes:** `id`, `name`, `linkedin_profile`, `email`, `phone`, `location`, `headline`, `summary`
- **Professional Metrics:** `total_experience_months`, `followers_count` for filtering and analysis
- **Skills Data:** Extracted `inferred_skills` list for expertise mapping
- **Work History:** Detailed `experience_history` with company, title, description, dates, duration
- **Education:** `education_history` with institution, degree, and timeline information

### **Neo4j Graph Schema**
```cypher
// Person nodes with comprehensive attributes
(:Person {id, name, email, phone, location, headline, summary, 
          followers_count, total_experience_months})

// Relationships with rich job description data
(:Person)-[:WORKS_AT {title, description, start_date, end_date, 
                      duration_months, location}]->(:Company)
(:Person)-[:HAS_SKILL]->(:Skill)
(:Person)-[:STUDIED_AT {degree, start_year, end_year}]->(:Institution)
```

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- Neo4j Database
- Required Python packages: `fastapi`, `neo4j`, `pandas`, `sentence-transformers`

### **Installation**

```bash
# Clone the repository
git clone https://github.com/Arjunheregeek/Connect.git
cd Connect

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Neo4j credentials and API key
```

### **Running the MCP Server**

```bash
# Start the MCP server
python -m mcp.server

# Server will be available at http://localhost:8000
# Health check: GET http://localhost:8000/health
# Tools list: GET http://localhost:8000/tools (requires API key)
```

### **MCP Client Configuration**

Add to your MCP client configuration:
```json
{
  "connect-mcp": {
    "command": "python",
    "args": ["-m", "mcp.server"],
    "cwd": "/path/to/Connect",
    "env": {
      "CONNECT_API_KEY": "your-api-key-here"
    }
  }
}
```

## 📡 API Usage

### **Authentication**
All API calls require the `X-API-Key` header:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/tools
```

### **Example MCP Requests**

**Find AI/ML Experts:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "find_technical_skills_in_descriptions",
    "arguments": {
      "tech_keywords": ["machine learning", "AI", "computer vision"],
      "limit": 10
    }
  }
}
```

**Analyze Career Progression:**
```json
{
  "jsonrpc": "2.0",
  "id": "2", 
  "method": "tools/call",
  "params": {
    "name": "analyze_career_progression",
    "arguments": {
      "person_name": "John Smith"
    }
  }
}
```

## 🔧 Performance Features

- **Multi-tier Caching:** 50%+ hit rate with configurable TTL
- **Connection Pooling:** Optimized Neo4j connections
- **Input Validation:** Comprehensive parameter validation
- **Error Handling:** Graceful error recovery and logging
- **Security:** API key authentication with configurable security headers

## 📁 Project Structure

```
Connect/
├── mcp/                    # MCP Server Implementation
│   ├── server.py          # FastAPI server
│   ├── handlers/          # MCP request handlers
│   ├── services/          # Bridge services
│   ├── schemas/           # Tool schemas
│   ├── utils/             # Utilities (caching, security, validation)
│   └── config/            # Configuration management
├── src/                   # Core graph operations
│   ├── graph_db.py        # Neo4j connection manager
│   ├── query.py           # Graph query methods
│   └── natural_language_search.py  # AI-powered search
├── Data/                  # Dataset files
├── Pre_processing/        # Data processing scripts
└── docs/                  # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for LangGraph Agents** - Enabling intelligent professional network analysis and career insights through standardized MCP protocol integration.