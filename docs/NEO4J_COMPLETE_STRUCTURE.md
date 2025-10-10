# Neo4j Knowledge Graph - Complete Structure Report

## 📊 Overview

**Total Dataset**: 164 profiles with 35 attributes each
**Database Type**: Neo4j Graph Database
**Node Types**: 3
**Relationship Types**: 3
**Estimated Total Nodes**: 300-450
**Estimated Total Relationships**: 800-1,500

---

## 🎯 Node Types and Properties

### 1. Person Node 👤
**Label**: `Person`
**Count**: 164 nodes (one per profile)

#### Properties:
```
Person {
  // IDENTITY PROPERTIES (5)
  person_id: Integer                   // Unique: 98905076, 98669998, etc.
  name: String                         // Full name
  email: String                        // Email address (58.5% coverage)
  phone: String                        // Phone number
  linkedin_profile: String             // LinkedIn URL
  
  // LOCATION (1)
  current_location: String             // "Bengaluru, Karnataka, India"
  
  // PROFILE PROPERTIES (2)
  headline: String                     // Professional headline
  summary: String                      // Bio/summary text
  
  // SCORING PROPERTIES (4)
  followers_count: Float               // LinkedIn follower count
  trustworthiness_score: Integer       // Trust score
  perceived_expertise_level: Integer   // Expertise level score
  competence_score: Integer            // Competence score
  
  // PROFESSIONAL PROPERTIES (8)
  current_title: String                // Current job title
  current_company: String              // Current employer
  industry: String                     // Industry sector
  seniority_level: String              // "Founder", "Senior", "Junior", etc.
  years_of_experience: Float           // Years of experience
  employment_type: String              // "Full-time Job", "Startup/Self-employed", etc.
  professional_status: String          // "Actively Employed", "Founder/Entrepreneur", etc.
  primary_expertise: String            // Main skill area
  total_experience_months: Float       // Total months of experience
  
  // SKILL PROPERTIES (3) - Arrays for fast access
  technical_skills: [String]           // ["Python", "Machine Learning", "AWS"]
  secondary_skills: [String]           // ["Leadership", "Communication", "Strategy"]
  domain_knowledge: [String]           // ["FinTech", "AI & ML", "HealthTech"]
  
  // EDUCATION (1)
  degrees: [String]                    // ["B.Tech", "MBA", "PhD"]
  
  // ASPIRATIONAL PROPERTIES (7) - For future enrichment
  current_goals: String                // Career/project goals
  current_challenges: String           // Challenges they face
  resources_needed: String             // What they're seeking
  availability_hiring: Boolean         // Open to hiring?
  availability_roles: Boolean          // Looking for roles?
  availability_cofounder: Boolean      // Seeking co-founder?
  availability_advisory: Boolean       // Available for advisory?
  
  // METADATA
  updated_at: DateTime                 // Last update timestamp
}
```

**Note**: All data is stored in Person node as properties. Company and Institution are separate nodes only for relationship purposes.

**Total Person Properties**: 35 properties per node

---

### 2. Company Node 🏢
**Label**: `Company`
**Estimated Count**: 100-200 nodes (unique companies from current + past roles)

#### Properties:
```
Company {
  // IDENTITY
  name: String                         // UNIQUE: Company name
  
  // METADATA
  created_at: DateTime
}
```

**Purpose**: Lightweight nodes for relationship connections only. All job details (role, dates, etc.) stored on relationships.

**Sources**: 
- `current_company` column → CURRENTLY_WORKS_AT relationship
- `experience_history` column (JSON array) → Parse to extract all companies and create relationships

---

### 3. Institution Node 🎓
**Label**: `Institution`
**Estimated Count**: 50-100 nodes (unique educational institutions)

#### Properties:
```
Institution {
  // IDENTITY
  name: String                         // UNIQUE: Institution name
  
  // METADATA
  created_at: DateTime
}
```

**Purpose**: Lightweight nodes for education relationships. All degree details (field, years) stored on relationships.

**Sources**: 
- `degrees` column → Array stored in Person node
- `education_history` column (JSON array) → Parse to create Institution nodes and STUDIED_AT relationships

---

## 🔗 Relationship Types

### 1. CURRENTLY_WORKS_AT (Current Employment)
**Direction**: `(Person)-[:CURRENTLY_WORKS_AT]->(Company)`
**Count**: ~164 relationships (one per person, if current_company exists)

#### Properties:
```
CURRENTLY_WORKS_AT {
  role: String                         // Job title
  start_date: String                   // When they started
  end_date: String                     // null for current jobs
  duration_months: Integer             // Duration in months
  description: String                  // Job description
  location: String                     // Office location
  is_current: Boolean                  // Always true
  created_at: DateTime
}
```

**Example**:
```cypher
(Person {name: "John Doe"})-[:CURRENTLY_WORKS_AT {role: "Senior Engineer", is_current: true}]->(Company {name: "Google"})
```

---

### 2. PREVIOUSLY_WORKED_AT (Past Employment)
**Direction**: `(Person)-[:PREVIOUSLY_WORKED_AT]->(Company)`
**Count**: ~500-1000 relationships (multiple per person from experience_history)

#### Properties:
```
PREVIOUSLY_WORKED_AT {
  role: String                         // Job title
  start_date: String                   // Start date
  end_date: String                     // End date
  duration_months: Integer             // Duration in months
  description: String                  // Job description
  location: String                     // Office location
  is_current: Boolean                  // Always false
  created_at: DateTime
}
```

**Example**:
```cypher
(Person {name: "John Doe"})-[:PREVIOUSLY_WORKED_AT {role: "Engineer", end_date: "2022-01"}]->(Company {name: "Microsoft"})
(Person {name: "John Doe"})-[:PREVIOUSLY_WORKED_AT {role: "Intern", end_date: "2020-06"}]->(Company {name: "Amazon"})
```

**Note**: One person can have multiple PREVIOUSLY_WORKED_AT relationships (one per previous company)

---

### 3. STUDIED_AT
**Direction**: `(Person)-[:STUDIED_AT]->(Institution)`
**Count**: ~164-300 relationships (some people have multiple degrees)

#### Properties:
```
STUDIED_AT {
  degree: String                       // "B.Tech., Mechanical Engineering" (includes field)
  start_year: Integer                  // Start year
  end_year: Integer                    // Graduation year
  created_at: DateTime
}
```

**Source**: `education_history` column (JSON array) and `degrees` column (string list)

**Example education_history format**:
```json
[{
  "institution_name": "Indian Institute of Technology, Bombay",
  "institution_url": "https://www.linkedin.com/school/...",
  "degree": "B.Tech., Mechanical Engineering",
  "start_year": 2021,
  "end_year": 2025
}]
```

---

## 🔐 Indexes and Constraints

### UNIQUE Constraints (Prevent Duplicates + Fast Lookup)
```cypher
// Person nodes
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

CREATE CONSTRAINT person_email_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.email IS UNIQUE;

CREATE CONSTRAINT person_linkedin_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.linkedin_profile IS UNIQUE;

// Company nodes
CREATE CONSTRAINT company_name_unique IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;

// Institution nodes
CREATE CONSTRAINT institution_name_unique IF NOT EXISTS
FOR (i:Institution) REQUIRE i.name IS UNIQUE;
```

### Regular Indexes (Fast Search)
```cypher
// Person properties frequently searched
CREATE INDEX person_name_idx IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX person_seniority_idx IF NOT EXISTS FOR (p:Person) ON (p.seniority);
CREATE INDEX person_expertise_idx IF NOT EXISTS FOR (p:Person) ON (p.primary_expertise);
CREATE INDEX person_industry_idx IF NOT EXISTS FOR (p:Person) ON (p.industry);

// Company properties
CREATE INDEX company_industry_idx IF NOT EXISTS FOR (c:Company) ON (c.industry);
```

### Full-Text Search Indexes (Text Search)
```cypher
// For natural language search
CREATE FULLTEXT INDEX person_text_search IF NOT EXISTS
FOR (p:Person) ON EACH [p.headline, p.summary, p.name];
```

---

## 📈 Visual Graph Structure

### Complete Graph Pattern:
```
                    ┌─────────────┐
                    │  Company    │
                    │  (100-200)  │
                    └─────────────┘
                           ▲
                           │ CURRENTLY_WORKS_AT (164)
                           │ PREVIOUSLY_WORKED_AT (500-1000)
                           │
                    ┌──────┴──────┐
                    │             │
            ┌───────────────┐     │
            │    Person     │     │
            │     (164)     │     │
            │               │     │
            │ Properties:   │     │
            │ • Skills []   │     │
            │ • Location    │     │
            │ • Degrees []  │     │
            │ • All data    │     │
            └───────────────┘     │
                    │             │
                    │ STUDIED_AT  │
                    │ (164-300)   │
                    ▼             │
            ┌──────────────┐      │
            │ Institution  │◄─────┘
            │  (50-100)    │
            └──────────────┘
```

**Note**: Person node is "fat" - contains all profile data as properties. Company and Institution are "thin" - just names for relationships.

---

## 🎯 Example: Single Person Node in Graph

Here's how one complete profile looks in the graph:

```
Person: "Ashray Malhotra" {
  person_id: 98905076
  name: "Ashray Malhotra"
  email: "amalhotra@adobe.com"
  phone: "9757163031"
  linkedin_profile: "https://www.linkedin.com/in/ashraymalhotra"
  current_location: "Bengaluru, Karnataka, India"
  headline: "Adobe | ex-Co-Founder, CEO @ Rephrase.ai | Forbes 30 Under 30 Asia"
  summary: "Building bleeding edge Generative AI Video products since 2019."
  followers_count: 25383.0
  trustworthiness_score: 1
  perceived_expertise_level: 88
  competence_score: 90
  current_title: "Product"
  current_company: "Adobe"
  industry: "Technology & Software"
  seniority_level: "Founder"
  years_of_experience: 12.2
  employment_type: "Full-time Job"
  professional_status: "Actively Employed"
  primary_expertise: "AI & ML"
  total_experience_months: 146.0
  technical_skills: ["Generative AI", "API Development", "Lipsync Technology", "Computer Vision", "Machine Learning"]
  secondary_skills: ["Leadership", "Strategic Planning", "Entrepreneurship", "Innovation"]
  domain_knowledge: ["Media & Entertainment", "AI & ML", "HealthTech", "Consumer Tech"]
  degrees: ["B.Tech., M.Tech"]
  current_goals: null
  availability_cofounder: null
}
    │
    ├─[:CURRENTLY_WORKS_AT {role: "Product", is_current: true}]───► Company: "Adobe"
    │
    ├─[:PREVIOUSLY_WORKED_AT {role: "Founder", end_date: "November 2023"}]───► Company: "Rephrase.ai"
    ├─[:PREVIOUSLY_WORKED_AT {role: "Member Company", end_date: "Oct 2023"}]─► Company: "Techstars"
    ├─[:PREVIOUSLY_WORKED_AT {role: "Founder", end_date: "June 2018"}]───────► Company: "SoundRex"
    │
    └─[:STUDIED_AT {degree: "B.Tech., M.Tech, Electrical and Electronics Engineering", start_year: 2011, end_year: 2016}]─► Institution: "IIT Bombay"
```

---

## 🔍 Common Query Patterns

### 1. Find People by Technical Skill
```cypher
MATCH (p:Person)
WHERE "Python" IN p.technical_skills
RETURN p.name, p.current_title, p.email, p.technical_skills
LIMIT 20;
```

### 2. Find People by Any Skill (technical, secondary, or domain)
```cypher
MATCH (p:Person)
WHERE "Machine Learning" IN p.technical_skills 
   OR "Machine Learning" IN p.secondary_skills
   OR "Machine Learning" IN p.domain_knowledge
RETURN p.name, p.current_title, p.email
LIMIT 20;
```

### 3. Find People in Specific Location with Skills
```cypher
MATCH (p:Person)
WHERE p.current_location CONTAINS "Bengaluru"
  AND "Python" IN p.technical_skills
RETURN p.name, p.current_title, p.email, p.technical_skills
LIMIT 10;
```

### 3. Find People in Specific Location with Skills
```cypher
MATCH (p:Person)
WHERE p.current_location CONTAINS "Bengaluru"
  AND "Python" IN p.technical_skills
RETURN p.name, p.current_title, p.email, p.technical_skills
LIMIT 10;
```

### 4. Find Alumni Network
```cypher
MATCH (p:Person)-[:STUDIED_AT]->(i:Institution {name: "IIT Bombay"})
RETURN p.name, p.current_company, p.email, p.technical_skills
ORDER BY p.years_of_experience DESC;
```

### 5. Find Co-founders with Complementary Skills
```cypher
MATCH (p1:Person), (p2:Person)
WHERE p1.availability_cofounder = true 
  AND p2.availability_cofounder = true
  AND p1 <> p2
  AND p1.current_location CONTAINS "Bengaluru"
  AND p2.current_location CONTAINS "Bengaluru"
  AND ANY(skill IN p1.technical_skills WHERE skill IN ["Python", "AI", "ML"])
  AND ANY(skill IN p2.secondary_skills WHERE skill IN ["Leadership", "Business", "Marketing"])
RETURN p1.name, p2.name, p1.technical_skills, p2.secondary_skills, p1.email, p2.email
LIMIT 10;
```

### 6. Find People Who Worked at Same Company
```cypher
MATCH (p1:Person)-[:PREVIOUSLY_WORKED_AT|CURRENTLY_WORKS_AT]->(c:Company {name: "Google"})
MATCH (p2:Person)-[:PREVIOUSLY_WORKED_AT|CURRENTLY_WORKS_AT]->(c)
WHERE p1 <> p2
RETURN p1.name, p2.name, c.name
LIMIT 50;
```

### 6. Find People Who Worked at Same Company
```cypher
MATCH (p1:Person)-[:PREVIOUSLY_WORKED_AT|CURRENTLY_WORKS_AT]->(c:Company {name: "Google"})
MATCH (p2:Person)-[:PREVIOUSLY_WORKED_AT|CURRENTLY_WORKS_AT]->(c)
WHERE p1 <> p2
RETURN p1.name, p2.name, c.name, p1.technical_skills, p2.technical_skills
LIMIT 50;
```

### 7. Find Skill Co-occurrence (What skills appear together?)
```cypher
MATCH (p:Person)
WHERE "Python" IN p.technical_skills
UNWIND p.technical_skills AS skill
WITH skill, COUNT(*) AS count
WHERE skill <> "Python"
RETURN skill, count
ORDER BY count DESC
LIMIT 10;
```

### 8. Find People by Full-Text Search
```cypher
CALL db.index.fulltext.queryNodes("person_text_search", "machine learning AI expert")
YIELD node, score
RETURN node.name, node.headline, score
ORDER BY score DESC
LIMIT 10;
```

---

## 📊 Database Statistics (Expected)

| Metric | Count |
|--------|-------|
| Total Nodes | 300-450 |
| - Person Nodes | 164 |
| - Company Nodes | 100-200 |
| - Institution Nodes | 50-100 |
| **Total Relationships** | **800-1,500** |
| - CURRENTLY_WORKS_AT | 164 |
| - PREVIOUSLY_WORKED_AT | 500-1,000 |
| - STUDIED_AT | 164-300 |
| **Total Properties** | **5,700+** (35 per Person × 164) |
| **Indexes** | 6 |
| **Constraints** | 5 |

---

## 🚀 Implementation Checklist

### Phase 1: Data Import
- [ ] Read CSV file with pandas
- [ ] Create Person nodes with all 32 properties
- [ ] Extract unique companies → Create Company nodes
- [ ] Extract unique skills → Create Skill nodes
- [ ] Extract unique institutions → Create Institution nodes
- [ ] Extract unique locations → Create Location nodes

### Phase 2: Relationship Creation
- [ ] Create CURRENTLY_WORKS_AT relationships (current_company)
- [ ] Create PREVIOUSLY_WORKED_AT relationships (experience_history)
- [ ] Parse and create HAS_TECHNICAL_SKILL relationships
- [ ] Parse and create HAS_SECONDARY_SKILL relationships
- [ ] Parse and create HAS_DOMAIN_KNOWLEDGE relationships
- [ ] Parse and create STUDIED_AT relationships
- [ ] Create LOCATED_IN relationships

### Phase 3: Optimization
- [ ] Create UNIQUE constraints on all key properties
- [ ] Create regular indexes on frequently searched properties
- [ ] Create full-text search indexes
- [ ] Run ANALYZE to update query planner statistics

### Phase 4: Validation
- [ ] Verify node counts match expectations
- [ ] Verify relationship counts
- [ ] Test sample queries for correctness
- [ ] Performance test on common query patterns

---

## 📝 Key Design Decisions

### 1. **Hybrid Skills Storage**
- **Properties**: `technical_skills_list`, `secondary_skills_list`, `domain_knowledge_list` (arrays)
  - Advantage: Fast inline access, no JOIN needed
  - Use Case: Quick filtering, simple queries
  
- **Relationships**: `HAS_TECHNICAL_SKILL`, `HAS_SECONDARY_SKILL`, `HAS_DOMAIN_KNOWLEDGE`
  - Advantage: Graph traversal, skill analytics, recommendations
  - Use Case: Complex queries, graph algorithms, co-occurrence analysis

### 2. **Separate Work Relationships**
- **CURRENTLY_WORKS_AT**: Current employment only (is_current: true)
- **PREVIOUSLY_WORKED_AT**: All past employment (is_current: false)
- Reason: Clear distinction, easier to query current vs past

### 3. **Normalized Entities**
- Companies, Skills, Institutions, Locations are separate nodes
- Reason: Avoid data duplication, enable network analysis (alumni networks, skill clustering)

### 4. **Null Values for Aspirational Attributes**
- 7 attributes currently null (current_goals, challenges, availability flags)
- Reason: Better than missing columns, allows future enrichment, maintains schema consistency

### 5. **Comprehensive Indexing**
- UNIQUE constraints prevent duplicates
- Regular indexes speed up common searches (100-1000x faster)
- Full-text indexes enable natural language search

---

## 🎓 Graph Database Benefits

### Traditional Database (SQL)
```sql
SELECT * FROM persons 
WHERE technical_skills LIKE '%Python%' 
  AND city = 'Bangalore'
  AND EXISTS (SELECT 1 FROM education WHERE university = 'Stanford');
```
❌ Multiple JOINs, slow, complex

### Graph Database (Neo4j)
```cypher
MATCH (p:Person)-[:LOCATED_IN]->(l {city: "Bangalore"})
MATCH (p)-[:HAS_TECHNICAL_SKILL]->(s {name: "Python"})
MATCH (p)-[:STUDIED_AT]->(i {name: "Stanford"})
RETURN p;
```
✅ Natural, fast, follows relationships

### Advanced Graph Queries (Impossible in SQL)
```cypher
// Find shortest connection path between two people
MATCH path = shortestPath(
  (p1:Person {name: "John"})-[*..5]-(p2:Person {name: "Jane"})
)
RETURN path;

// Run PageRank to find most influential people
CALL gds.pageRank.stream({
  nodeProjection: 'Person',
  relationshipProjection: 'KNOWS'
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name, score
ORDER BY score DESC;
```

---

## 📌 Summary

This Neo4j knowledge graph provides a **simple, performant** structure for:
- ✅ **Person Discovery**: Find people by skills (arrays), location (string), education, company
- ✅ **Network Analysis**: Alumni networks, co-worker connections
- ✅ **Recommendations**: Find similar people, complementary co-founders
- ✅ **Career Insights**: Track career paths through company relationships
- ✅ **Hiring/Matching**: Match opportunities with availability flags and skills
- ✅ **Fast Queries**: All person data in one node - no joins needed

**Total Structure**:
- **3 Node Types**: Person (fat node with all data), Company, Institution (thin nodes for relationships)
- **3 Relationship Types**: CURRENTLY_WORKS_AT, PREVIOUSLY_WORKED_AT, STUDIED_AT
- **35 Properties per Person**: Complete profile including skills, location, degrees as arrays
- **6 Indexes**: Optimized for fast retrieval
- **Property Storage**: Skills, location, degrees stored as Person properties for fast access

The database is ready for import from `Final_Merged_Knowledge_Graph.csv` (164 profiles, 35 columns).

---

*Generated: October 2025*
*Dataset: Final_Merged_Knowledge_Graph.csv*
*Profiles: 164 | Attributes: 35 | Graph Structure: Simplified for Performance*
