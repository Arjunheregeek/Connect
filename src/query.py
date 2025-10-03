# --- src/query.py ---

class QueryManager:
    """
    Handles all read-only queries to the Neo4j database to retrieve
    information from the knowledge graph.
    """
    def __init__(self, db_driver):
        """
        Initializes the query manager with an active database driver.
        """
        self.db = db_driver

    def find_person_by_name(self, name):
        """
        Finds a person by their full name (case-insensitive).
        """
        query = """
        MATCH (p:Person)
        WHERE toLower(p.name) CONTAINS toLower($name)
        RETURN p.name as name, p.headline as headline, p.linkedin_profile as profile
        """
        return self.db.execute_query(query, params={"name": name})

    def find_people_by_skill(self, skill):
        """
        Finds all people who have a specific skill.
        """
        query = """
        MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
        WHERE s.name = toLower($skill)
        RETURN p.name as name, p.headline as headline
        ORDER BY name
        """
        return self.db.execute_query(query, params={"skill": skill})

    def find_people_by_company(self, company_name):
        """
        Finds all people who have worked at a specific company.
        """
        query = """
        MATCH (p:Person)-[:WORKS_AT]->(c:Company)
        WHERE toLower(c.name) CONTAINS toLower($company_name)
        RETURN DISTINCT p.name as name, p.headline as headline
        ORDER BY name
        """
        return self.db.execute_query(query, params={"company_name": company_name})
    
    def find_colleagues_at_company(self, person_id, company_name):
        """
        Finds who a specific person worked with at a given company.
        """
        query = """
        MATCH (p1:Person {id: $person_id})-[:WORKS_AT]->(c:Company)<-[:WORKS_AT]-(p2:Person)
        WHERE toLower(c.name) CONTAINS toLower($company_name) AND p1 <> p2
        RETURN p2.name as colleague_name, p2.headline as colleague_headline
        ORDER BY colleague_name
        """
        return self.db.execute_query(query, params={"person_id": person_id, "company_name": company_name})

    def find_people_by_institution(self, institution_name):
        """
        Finds all people who studied at a specific institution.
        """
        query = """
        MATCH (p:Person)-[:STUDIED_AT]->(i:Institution)
        WHERE toLower(i.name) CONTAINS toLower($institution_name)
        RETURN DISTINCT p.name as name, p.headline as headline
        ORDER BY name
        """
        return self.db.execute_query(query, params={"institution_name": institution_name})

    def find_people_by_location(self, location):
        """
        Finds all people in a specific location.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower(p.location) CONTAINS toLower($location)
        RETURN p.name as name, p.headline as headline, p.location as location
        ORDER BY name
        """
        return self.db.execute_query(query, params={"location": location})

    def get_person_skills(self, person_name):
        """
        Gets all skills for a specific person.
        """
        query = """
        MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
        WHERE toLower(p.name) CONTAINS toLower($person_name)
        RETURN p.name as person_name, collect(s.name) as skills
        """
        return self.db.execute_query(query, params={"person_name": person_name})

    def find_people_with_multiple_skills(self, skills_list, match_type="any"):
        """
        Finds people who have multiple skills.
        
        Args:
            skills_list: List of skills to search for
            match_type: "any" to match any skill, "all" to match all skills
        """
        if match_type == "all":
            # Find people who have ALL the specified skills
            query = """
            MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
            WHERE s.name IN $skills_list
            WITH p, count(DISTINCT s.name) as skill_count
            WHERE skill_count = $required_count
            RETURN p.name as name, p.headline as headline
            ORDER BY name
            """
            return self.db.execute_query(query, params={
                "skills_list": [skill.lower() for skill in skills_list],
                "required_count": len(skills_list)
            })
        else:
            # Find people who have ANY of the specified skills
            query = """
            MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
            WHERE s.name IN $skills_list
            RETURN DISTINCT p.name as name, p.headline as headline
            ORDER BY name
            """
            return self.db.execute_query(query, params={
                "skills_list": [skill.lower() for skill in skills_list]
            })

    def get_person_colleagues(self, person_name):
        """
        Gets all colleagues of a person across all companies they worked at.
        """
        query = """
        MATCH (p1:Person)-[:WORKS_AT]->(c:Company)<-[:WORKS_AT]-(p2:Person)
        WHERE toLower(p1.name) CONTAINS toLower($person_name) AND p1 <> p2
        RETURN p2.name as colleague_name, p2.headline as colleague_headline, c.name as company_name
        ORDER BY company_name, colleague_name
        """
        return self.db.execute_query(query, params={"person_name": person_name})

    def find_people_by_experience_level(self, min_months=None, max_months=None):
        """
        Finds people based on their total experience in months.
        """
        conditions = []
        params = {}
        
        if min_months is not None:
            conditions.append("p.total_experience_months >= $min_months")
            params["min_months"] = min_months
            
        if max_months is not None:
            conditions.append("p.total_experience_months <= $max_months")
            params["max_months"] = max_months
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
        MATCH (p:Person)
        {where_clause}
        RETURN p.name as name, p.headline as headline, p.total_experience_months as experience_months
        ORDER BY p.total_experience_months DESC
        """
        return self.db.execute_query(query, params=params)

    def get_company_employees(self, company_name):
        """
        Gets all employees (past and present) of a specific company.
        """
        query = """
        MATCH (p:Person)-[:WORKS_AT]->(c:Company)
        WHERE toLower(c.name) CONTAINS toLower($company_name)
        RETURN p.name as name, p.headline as headline, c.name as company_name
        ORDER BY name
        """
        return self.db.execute_query(query, params={"company_name": company_name})

    def get_skill_popularity(self, limit=20):
        """
        Gets the most popular skills by counting how many people have each skill.
        """
        query = """
        MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
        RETURN s.name as skill_name, count(p) as person_count
        ORDER BY person_count DESC
        LIMIT $limit
        """
        return self.db.execute_query(query, params={"limit": limit})

    def get_person_details(self, person_name):
        """
        Gets comprehensive details about a person including skills, companies, and education.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower(p.name) CONTAINS toLower($person_name)
        OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (p)-[:WORKS_AT]->(c:Company)
        OPTIONAL MATCH (p)-[:STUDIED_AT]->(i:Institution)
        RETURN p.name as name, p.headline as headline, p.location as location,
               p.linkedin_profile as linkedin_profile, p.email as email,
               p.total_experience_months as experience_months,
               collect(DISTINCT s.name) as skills,
               collect(DISTINCT c.name) as companies,
               collect(DISTINCT i.name) as institutions
        """
        return self.db.execute_query(query, params={"person_name": person_name})

    def get_person_job_descriptions(self, person_name):
        """
        Gets all job descriptions for a person with company and role details.
        This is the foundation for technical skill discovery, behavioral analysis, and career progression.
        """
        query = """
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE toLower(p.name) CONTAINS toLower($person_name)
        RETURN p.name as person_name,
               c.name as company_name,
               r.title as job_title,
               r.description as job_description,
               r.start_date as start_date,
               r.end_date as end_date,
               r.duration_months as duration_months,
               r.location as job_location
        ORDER BY r.start_date DESC
        """
        return self.db.execute_query(query, params={"person_name": person_name})
    
    def search_job_descriptions_by_keywords(self, keywords, match_type="any"):
        """
        Search for people based on keywords in their job descriptions.
        Useful for finding technical skills, behavioral patterns, or specific experience.
        
        Args:
            keywords: List of keywords to search for in job descriptions
            match_type: "any" to match any keyword, "all" to match all keywords
        """
        if match_type == "all":
            # All keywords must be present in job description
            conditions = [f"toLower(r.description) CONTAINS toLower(${i})" for i in range(len(keywords))]
            where_clause = " AND ".join(conditions)
            params = {str(i): keyword for i, keyword in enumerate(keywords)}
        else:
            # Any keyword can be present
            conditions = [f"toLower(r.description) CONTAINS toLower(${i})" for i in range(len(keywords))]
            where_clause = " OR ".join(conditions)
            params = {str(i): keyword for i, keyword in enumerate(keywords)}
        
        query = f"""
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN DISTINCT p.name as person_name, p.headline as headline,
               c.name as company_name, r.title as job_title,
               r.description as job_description
        ORDER BY p.name
        """
        return self.db.execute_query(query, params=params)
    
    def find_technical_skills_in_descriptions(self, tech_keywords):
        """
        Find people who mention specific technical skills in their job descriptions.
        Goes beyond structured skills to find contextual technical mentions.
        
        Args:
            tech_keywords: List of technical terms to search for (e.g., ["python", "kubernetes", "machine learning"])
        """
        # Create case-insensitive search conditions
        conditions = [f"toLower(r.description) CONTAINS toLower('{keyword}')" for keyword in tech_keywords]
        where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN p.name as person_name, p.headline as headline,
               c.name as company_name, r.title as job_title,
               r.description as job_description,
               r.start_date as start_date, r.end_date as end_date
        ORDER BY r.start_date DESC
        """
        return self.db.execute_query(query)
    
    def find_leadership_indicators(self):
        """
        Find people with leadership indicators in their job descriptions.
        Looks for management, team lead, and leadership-related keywords.
        """
        leadership_keywords = [
            "led team", "managed team", "team lead", "people manager", "director",
            "head of", "vp ", "vice president", "chief", "cto", "ceo", "cfo",
            "managed", "supervised", "mentored", "coached", "led", "leadership",
            "cross-functional", "stakeholder", "strategic", "vision", "roadmap"
        ]
        
        conditions = [f"toLower(r.description) CONTAINS '{keyword}'" for keyword in leadership_keywords]
        where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN p.name as person_name, p.headline as headline,
               c.name as company_name, r.title as job_title,
               r.description as job_description,
               r.duration_months as duration_months
        ORDER BY r.duration_months DESC
        """
        return self.db.execute_query(query)
    
    def find_achievement_patterns(self):
        """
        Find people with quantifiable achievements in their job descriptions.
        Looks for metrics, improvements, and measurable impact.
        """
        achievement_keywords = [
            "increased", "improved", "reduced", "optimized", "enhanced", "delivered",
            "achieved", "exceeded", "saved", "generated", "grew", "scaled",
            "%", "percent", "million", "billion", "k ", "x ", "times",
            "faster", "efficiency", "performance", "revenue", "cost"
        ]
        
        conditions = [f"toLower(r.description) CONTAINS '{keyword}'" for keyword in achievement_keywords]
        where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN p.name as person_name, p.headline as headline,
               c.name as company_name, r.title as job_title,
               r.description as job_description,
               r.start_date as start_date, r.end_date as end_date
        ORDER BY p.name
        """
        return self.db.execute_query(query)
    
    def analyze_career_progression(self, person_name):
        """
        Analyze a person's career progression by examining job titles and descriptions over time.
        Shows how their roles, responsibilities, and seniority evolved.
        """
        query = """
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE toLower(p.name) CONTAINS toLower($person_name)
        RETURN p.name as person_name,
               c.name as company_name,
               r.title as job_title,
               r.description as job_description,
               r.start_date as start_date,
               r.end_date as end_date,
               r.duration_months as duration_months,
               r.location as job_location
        ORDER BY r.start_date ASC
        """
        return self.db.execute_query(query, params={"person_name": person_name})
    
    def find_domain_experts(self, domain_keywords):
        """
        Find people with deep domain expertise based on job description analysis.
        
        Args:
            domain_keywords: List of domain-specific terms (e.g., ["fintech", "healthcare", "e-commerce"])
        """
        conditions = [f"toLower(r.description) CONTAINS toLower('{keyword}')" for keyword in domain_keywords]
        where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        WITH p, count(r) as domain_jobs, collect(DISTINCT c.name) as companies,
             collect(DISTINCT r.title) as roles
        WHERE domain_jobs >= 2  // At least 2 jobs in the domain
        RETURN p.name as person_name, p.headline as headline,
               domain_jobs, companies, roles,
               p.total_experience_months as total_experience
        ORDER BY domain_jobs DESC, p.total_experience_months DESC
        """
        return self.db.execute_query(query)
    
    def find_similar_career_paths(self, reference_person_name, similarity_threshold=2):
        """
        Find people with similar career paths to a reference person.
        Compares job titles, companies, and progression patterns.
        
        Args:
            reference_person_name: The person to compare against
            similarity_threshold: Minimum number of similar elements (companies/roles)
        """
        query = """
        // Get reference person's career data
        MATCH (ref:Person)-[ref_r:WORKS_AT]->(ref_c:Company)
        WHERE toLower(ref.name) CONTAINS toLower($reference_name)
        WITH ref, collect(DISTINCT ref_c.name) as ref_companies, 
             collect(DISTINCT toLower(ref_r.title)) as ref_titles
        
        // Find people with overlapping companies or similar titles
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE p <> ref
        WITH ref, ref_companies, ref_titles, p,
             collect(DISTINCT c.name) as person_companies,
             collect(DISTINCT toLower(r.title)) as person_titles
        
        // Calculate similarity
        WITH ref, p, ref_companies, ref_titles, person_companies, person_titles,
             [x IN ref_companies WHERE x IN person_companies] as common_companies,
             [x IN ref_titles WHERE x IN person_titles] as common_titles
        
        WHERE size(common_companies) + size(common_titles) >= $threshold
        
        RETURN p.name as similar_person, p.headline as headline,
               common_companies, common_titles,
               size(common_companies) + size(common_titles) as similarity_score
        ORDER BY similarity_score DESC
        """
        return self.db.execute_query(query, params={
            "reference_name": reference_person_name,
            "threshold": similarity_threshold
        })
    
    def find_role_transition_patterns(self, from_role_keywords, to_role_keywords):
        """
        Find people who transitioned from one type of role to another.
        Useful for understanding career pivot patterns.
        
        Args:
            from_role_keywords: Keywords for the starting role type
            to_role_keywords: Keywords for the target role type
        """
        from_conditions = [f"toLower(r1.title) CONTAINS '{keyword}'" for keyword in from_role_keywords]
        to_conditions = [f"toLower(r2.title) CONTAINS '{keyword}'" for keyword in to_role_keywords] 
        
        from_clause = " OR ".join(from_conditions)
        to_clause = " OR ".join(to_conditions)
        
        query = f"""
        MATCH (p:Person)-[r1:WORKS_AT]->(c1:Company)
        MATCH (p)-[r2:WORKS_AT]->(c2:Company)
        WHERE r1.start_date < r2.start_date
          AND ({from_clause})
          AND ({to_clause})
        RETURN p.name as person_name, p.headline as headline,
               c1.name as from_company, r1.title as from_role, r1.start_date as from_start,
               c2.name as to_company, r2.title as to_role, r2.start_date as to_start,
               r1.description as from_description, r2.description as to_description
        ORDER BY r2.start_date DESC
        """
        return self.db.execute_query(query)
