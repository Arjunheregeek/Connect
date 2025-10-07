# Connect Agent Usage Guide

A comprehensive guide to using the Connect Agent for querying your people knowledge graph.

## Quick Start

### Basic Usage

```python
from app.agent_run import ask_sync

# Simple question
response = ask_sync("Find Python developers")
print(response)

# Company-specific search
response = ask_sync("Who works at Google?")
print(response)

# Skill-based search
response = ask_sync("Find React experts in San Francisco")
print(response)
```

### Detailed Responses

```python
from app.agent_run import ask_detailed_sync

result = ask_detailed_sync("Find data scientists")

print(f"Response: {result['response']}")
print(f"Tools used: {result['metadata']['tools_used']}")
print(f"Execution time: {result['metadata']['execution_time']:.2f}s")
print(f"Success: {result['success']}")
```

### Batch Processing

```python
from app.agent_run import batch_ask

questions = [
    "Find JavaScript developers",
    "Who are the project managers?", 
    "Find people at startups"
]

responses = batch_ask(questions)
for question, response in zip(questions, responses):
    print(f"Q: {question}")
    print(f"A: {response}\n")
```

## Advanced Features

### Conversation Management

```python
from app.agent_run import ask_sync

# Use conversation ID to maintain context  
conv_id = "my_session"

response1 = ask_sync("Find React developers", conv_id)
response2 = ask_sync("Which ones work at tech companies?", conv_id)
response3 = ask_sync("Show me their contact info", conv_id)
```

### Session Analytics

```python
from app.agent_run import get_session_summary, get_agent_info

# Get current session statistics
summary = get_session_summary()
print(f"Questions asked: {summary['total_questions']}")
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Average time: {summary['average_execution_time']:.2f}s")

# Get agent capabilities and info
info = get_agent_info()
print(f"Agent: {info['agent_type']}")
print(f"Capabilities: {info['capabilities']}")
```

### Async Operations

```python
import asyncio
from app.agent_run import get_agent

async def async_example():
    agent = get_agent()
    
    # Async version for better performance
    response = await agent.ask("Find software engineers")
    print(response)
    
    # Detailed async response
    result = await agent.ask_detailed("Find managers")
    print(f"Used tools: {result['metadata']['tools_used']}")

# Run async function
asyncio.run(async_example())
```

## Query Types & Examples

### 1. Person Search

```python
# By name
ask_sync("Find John Smith")
ask_sync("Look for people named Sarah")

# Partial name matching
ask_sync("Find anyone with last name Johnson")
ask_sync("People named Mike or Michael")
```

### 2. Skill-Based Search

```python
# Programming languages
ask_sync("Find Python developers")
ask_sync("Who knows JavaScript and React?")
ask_sync("Find full-stack developers")

# Technologies and frameworks
ask_sync("Find people with AWS experience")
ask_sync("Who knows Docker and Kubernetes?")
ask_sync("Find machine learning experts")

# Soft skills
ask_sync("Find project managers")
ask_sync("Who has leadership experience?")
ask_sync("Find people with communication skills")
```

### 3. Company & Location Search

```python
# By company
ask_sync("Who works at Google?")
ask_sync("Find Microsoft employees")
ask_sync("People at tech startups")

# By location
ask_sync("Find developers in San Francisco")
ask_sync("Who is based in New York?")
ask_sync("Remote workers in tech")

# Combined searches
ask_sync("Find Python developers at Google in California")
```

### 4. Role-Based Search

```python
# Job titles
ask_sync("Find software engineers")
ask_sync("Who are the data scientists?")
ask_sync("Find product managers")

# Seniority levels
ask_sync("Find senior developers")
ask_sync("Who are the engineering leads?")
ask_sync("Find junior developers")
```

### 5. Complex Queries

```python
# Multiple criteria
ask_sync("Find senior Python developers at tech companies in San Francisco")
ask_sync("Who are the React experts with startup experience?")

# Exclude criteria
ask_sync("Find developers who don't work at Google")
ask_sync("Python developers not in California")

# Comparative queries
ask_sync("Compare Python vs JavaScript developers")
ask_sync("Which companies have the most engineers?")
```

## Agent Features

### Simplified Architecture

The agent uses a streamlined approach:
- **Linear Workflow**: Planning → Execution → Synthesis (no cycles)
- **Real MCP Integration**: Direct connection to Neo4j knowledge graph with 1,992+ profiles
- **24+ Tools**: Comprehensive tool set for people search and analysis
- **No Retry Complexity**: Simplified error handling without retry loops

### Session Management

- **Conversation history** maintained per session
- **Context awareness** across related queries  
- **Performance tracking** and analytics
- **Easy session cleanup** when needed

### Data Access

- **1,992+ Professional Profiles** in Neo4j knowledge graph
- **Real-time Results**: Direct database queries through MCP server
- **Rich Profile Data**: Skills, companies, locations, roles, and more

## Error Handling

### Common Issues

```python
from app.agent_run import ask_sync

# Handle connection issues
try:
    response = ask_sync("Find developers")
except Exception as e:
    print(f"Error: {e}")
    # Check if MCP server is running
```

### Debugging

```python
from app.agent_run import ask_detailed_sync

# Get detailed info for debugging
result = ask_detailed_sync("problematic query")

if not result['success']:
    print(f"Error: {result['metadata'].get('error', 'Unknown error')}")
    print(f"Tools used: {result['metadata']['tools_used']}")
    print(f"Execution time: {result['metadata']['execution_time']:.2f}s")
```

## Performance Tips

### 1. Batch Similar Queries

```python
# Instead of multiple individual calls
questions = ["Find React devs", "Find Vue devs", "Find Angular devs"]
responses = batch_ask(questions)  # More efficient
```

### 2. Use Conversation Context

```python
from app.agent_run import ask_sync

# Maintain context for related queries
conv_id = "skill_search"
ask_sync("Find Python developers", conv_id)
ask_sync("Which ones have 5+ years experience?", conv_id)  # Uses context
```

### 3. Clear Sessions When Done

```python
from app.agent_run import clear_session

# Clear history to free memory
clear_session()
```

## Integration Examples

### Web Application

```python
from flask import Flask, request, jsonify
from app.agent_run import ask_sync, ask_detailed_sync

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search_people():
    query = request.json.get('query')
    result = ask_detailed_sync(query)
    
    return jsonify({
        'response': result['response'],
        'tools_used': result['metadata']['tools_used'],
        'execution_time': result['metadata']['execution_time'],
        'success': result['success']
    })

@app.route('/quick-search')
def quick_search():
    query = request.args.get('q')
    response = ask_sync(query)
    return {'response': response}
```

### CLI Tool

```python
#!/usr/bin/env python3
import sys
from app.agent_run import ask_sync

def main():
    if len(sys.argv) < 2:
        print("Usage: search.py 'your query here'")
        return
    
    query = ' '.join(sys.argv[1:])
    response = ask_sync(query)
    print(response)

if __name__ == "__main__":
    main()
```

### Jupyter Notebook

```python
# Cell 1: Setup
from app.agent_run import ask_sync, ask_detailed_sync, get_session_summary
import pandas as pd

# Cell 2: Basic search
response = ask_sync("Find data scientists at tech companies")
print(response)

# Cell 3: Detailed analysis
result = ask_detailed_sync("Find Python developers")
print(f"Found results in {result['metadata']['execution_time']:.2f}s")
print(f"Tools used: {result['metadata']['tools_used']}")

# Cell 4: Session analytics
summary = get_session_summary()
pd.DataFrame([summary])
```

## Configuration

### MCP Server Settings

Ensure your MCP server is configured in `mcp_client_config.json`:

```json
{
  "server_name": "connect_server",
  "command": "python",
  "args": ["-m", "mcp.server"],
  "env": {}
}
```

### Environment Variables

```bash
# Optional: Set Neo4j connection details
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

## Troubleshooting

### Common Issues

1. **"Connection refused"**
   - Ensure MCP server is running: `python -m mcp.server`
   - Check server configuration in `mcp_client_config.json`

2. **"No results found"**
   - Try broader search terms
   - Check if data exists in your knowledge graph (1,992+ profiles available)
   - Use detailed response to see tools used

3. **Slow responses**
   - Check Neo4j database performance
   - Use batch queries for multiple searches
   - Clear session history if very long

4. **Connection issues**
   - Ensure MCP server is running on localhost:8000
   - Check detailed response for error information
   - Verify Neo4j database is accessible

### Getting Help

```python
from app.agent_run import get_agent_info

# See agent capabilities and current status
info = get_agent_info()
print(info)
```

For more help, check the demo scripts:
```bash
# Interactive agent demo
python working_demo.py

# CLI usage
python app/agent_run.py "Find Python developers"

# Interactive mode
python app/agent_run.py
```