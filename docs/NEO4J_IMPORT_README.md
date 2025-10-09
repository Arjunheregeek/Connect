# Neo4j Knowledge Graph Import

This script imports LinkedIn profile data from CSV into a Neo4j graph database following an optimized structure.

## 📊 Graph Structure

### Node Types (3)
- **Person** (164 nodes) - All profile data stored as properties
- **Company** (50-100 nodes) - Organizations (for relationships only)
- **Institution** (50-100 nodes) - Educational institutions (for relationships only)

### Relationship Types (3)
- **CURRENTLY_WORKS_AT** - Current employment
- **PREVIOUSLY_WORKED_AT** - Past employment
- **STUDIED_AT** - Educational background

## 🚀 Quick Start

### 1. Set Up Neo4j

**Option A: Neo4j Desktop**
1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new database
3. Start the database
4. Note the connection details (bolt://localhost:7687 by default)

**Option B: Neo4j AuraDB (Cloud)**
1. Sign up at [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create a free instance
3. Download the credentials file
4. Note your connection URI and credentials

**Option C: Docker**
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    neo4j:latest
```

### 2. Set Environment Variables

Create a `.env` file or export variables:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

### 3. Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Install required packages
pip install neo4j pandas
```

### 4. Run the Import

```bash
python run_import.py
```

## 📝 What Gets Imported

For each profile in the CSV, the script:

1. ✅ Creates a **Person** node with 35+ properties including:
   - Identity (name, email, phone, LinkedIn)
   - Professional info (title, company, industry, seniority)
   - Skills as arrays (technical_skills, secondary_skills, domain_knowledge)
   - Location as string (current_location)
   - Scores (trustworthiness, expertise, competence)
   - Aspirational attributes (goals, challenges, availability flags)
   - Education (degrees as array)
   
2. ✅ Parses `experience_history` JSON to create **Company** nodes
3. ✅ Creates **CURRENTLY_WORKS_AT** or **PREVIOUSLY_WORKED_AT** relationships with job details
4. ✅ Parses `education_history` JSON to create **Institution** nodes
5. ✅ Creates **STUDIED_AT** relationships with degree information

## 📊 Expected Results

```
Nodes Created:
  • Person nodes:      164
  • Company nodes:     ~100-200
  • Institution nodes: ~50-100

Relationships Created:
  • CURRENTLY_WORKS_AT:    ~164
  • PREVIOUSLY_WORKED_AT:  ~500-1000
  • STUDIED_AT:            ~164-300

Total: ~800-1,500 relationships
```

## 🔍 Example Queries

After import, try these Cypher queries in Neo4j Browser:

### Find people by skill (skills stored as Person properties)
```cypher
MATCH (p:Person)
WHERE "machine learning" IN p.technical_skills
RETURN p.name, p.current_title, p.email
LIMIT 10;
```

### Find people in specific location with Python skills
```cypher
MATCH (p:Person)
WHERE p.current_location CONTAINS "Bengaluru"
  AND "Python" IN p.technical_skills
RETURN p.name, p.current_title, p.email, p.technical_skills
LIMIT 10;
```

### Find IIT Bombay alumni
```cypher
MATCH (p:Person)-[:STUDIED_AT]->(i:Institution)
WHERE i.name CONTAINS "IIT Bombay"
RETURN p.name, p.current_company, p.email
ORDER BY p.years_of_experience DESC;
```

### Find people currently working at a company
```cypher
MATCH (p:Person)-[r:CURRENTLY_WORKS_AT]->(c:Company {name: "Adobe"})
RETURN p.name, r.role, p.linkedin_profile;
```

### Find co-workers (people who worked at same company)
```cypher
MATCH (p1:Person)-[:PREVIOUSLY_WORKED_AT|CURRENTLY_WORKS_AT]->(c:Company)<-[:PREVIOUSLY_WORKED_AT|CURRENTLY_WORKS_AT]-(p2:Person)
WHERE p1 <> p2 AND c.name = "Google"
RETURN p1.name, p2.name, c.name
LIMIT 20;
```

### Find people with multiple skills
```cypher
MATCH (p:Person)
WHERE "Python" IN p.technical_skills
  AND "Machine Learning" IN p.technical_skills
  AND "Leadership" IN p.secondary_skills
RETURN p.name, p.current_title, p.technical_skills, p.secondary_skills
LIMIT 10;
```

### Find people available for co-founder opportunities
```cypher
MATCH (p:Person)
WHERE p.availability_cofounder = true
  AND p.current_location CONTAINS "Bengaluru"
RETURN p.name, p.current_title, p.technical_skills, p.domain_knowledge, p.email
LIMIT 10;
```

## 🐛 Troubleshooting

### Connection Error
```
❌ Failed to connect to Neo4j
```
**Solution**: Check that Neo4j is running and credentials are correct.

### Constraint Errors
```
⚠️ Constraint might already exist
```
**Solution**: This is normal if running import multiple times. Constraints are idempotent.

### Duplicate Data
If you run the import multiple times, data will be merged (not duplicated) thanks to MERGE statements.

To start fresh:
```cypher
// Delete all data (in Neo4j Browser)
MATCH (n) DETACH DELETE n;
```

## 📚 Architecture Details

See [`docs/NEO4J_COMPLETE_STRUCTURE.md`](docs/NEO4J_COMPLETE_STRUCTURE.md) for complete architecture documentation including:
- Detailed node properties
- Relationship properties
- Index strategies
- Query patterns
- Design decisions

## 🔧 Advanced Configuration

### Batch Size
For large datasets, modify the importer to use batching:
```python
# In importer.py, use UNWIND with batches
BATCH_SIZE = 100
```

### Custom CSV Path
```python
CSV_PATH = "path/to/your/data.csv"
```

### Additional Indexes
Add more indexes in `setup_constraints()` for frequently queried properties.

## 📖 Next Steps

1. ✅ Import complete? Great!
2. 🔍 Explore in Neo4j Browser at http://localhost:7474
3. 📊 Run the example queries above
4. 🛠️ Build your search/recommendation system
5. 📱 Connect your frontend application

## 🤝 Support

For issues or questions:
- Check Neo4j documentation: https://neo4j.com/docs/
- Review the architecture doc: `docs/NEO4J_COMPLETE_STRUCTURE.md`
- Neo4j Community: https://community.neo4j.com/
