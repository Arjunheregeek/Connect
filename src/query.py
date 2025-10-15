# --- src/query.py ---

class QueryManager:
    """
    Handles all read-only queries to the Neo4j database to retrieve
    information from the knowledge graph.
    Updated to work with the new simplified schema where skills are arrays
    and work relationships are split into CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT.
    """
    def __init__(self, db_driver):
        """
        Initializes the query manager with an active database driver.
        """
        self.db = db_driver

    def get_person_complete_profile(self, person_id=None, person_name=None):
        """
        Returns the complete profile for a person with essential fields only.
        Includes work history with job descriptions (education removed for token efficiency).
        Optimized to return only fields actually used by the synthesizer.
        
        Args:
            person_id: The unique person ID (preferred)
            person_name: The person's name (alternative identifier)
        """
        if person_id:
            match_clause = "MATCH (p:Person {person_id: $person_id})"
            params = {"person_id": person_id}
        elif person_name:
            match_clause = "MATCH (p:Person) WHERE toLower(p.name) CONTAINS toLower($person_name)"
            params = {"person_name": person_name}
        else:
            return {"error": "Must provide either person_id or person_name"}
        
        query = f"""
        {match_clause}
        
        // Get work history with job descriptions
        OPTIONAL MATCH (p)-[work:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WITH p, collect(DISTINCT {{
            company: c.name,
            title: work.role,
            
            
            
            
            location: work.location,
            is_current: work.is_current
        }}) as work_history
        
        // Return only essential 14 fields used by synthesizer
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.headline as headline,
            
            p.linkedin_profile as linkedin_profile,
            p.current_location as location,
            p.current_company as current_company,
            p.current_title as current_title,
            p.total_experience_months as total_experience_months,
            p.technical_skills as technical_skills,
            p.secondary_skills as secondary_skills,
            p.domain_knowledge as domain_knowledge,
            work_history
        """
        return self.db.execute_query(query, params=params)


    def find_person_by_name(self, name):
        """
        Finds a person by their full name (case-insensitive).
        Returns lightweight profile with person_id for agent tracking.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower(p.name) CONTAINS toLower($name)
        RETURN 
            p.person_id as person_id,
            p.name as name, 
            p.headline as headline,
            p.current_company as current_company,
            p.current_title as current_title
        """
        return self.db.execute_query(query, params={"name": name})


    def find_people_by_skill(self, skill):
        """
        Finds all people who have a specific skill.
        Skills are stored as arrays on Person nodes: technical_skills, secondary_skills, domain_knowledge.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower($skill) IN [s IN p.technical_skills | toLower(s)]
           OR toLower($skill) IN [s IN p.secondary_skills | toLower(s)]
           OR toLower($skill) IN [s IN p.domain_knowledge | toLower(s)]
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.current_company as current_company,
            p.current_title as current_title
        ORDER BY name
        """
        return self.db.execute_query(query, params={"skill": skill})


    def find_people_by_technical_skill(self, skill):
        """
        Finds all people who have a specific technical skill.
        Searches only the technical_skills array property on Person nodes.
        Use this for technical skills like Python, AWS, Machine Learning, etc.
        Returns lightweight profile with person_id and technical skills.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower($skill) IN [s IN p.technical_skills | toLower(s)]
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.headline as headline,
            p.technical_skills as technical_skills
        ORDER BY name
        """
        return self.db.execute_query(query, params={"skill": skill})


    def find_people_by_secondary_skill(self, skill):
        """
        Finds all people who have a specific secondary skill.
        Searches only the secondary_skills array property on Person nodes.
        Use this for soft skills like Leadership, Communication, Project Management, etc.
        Returns lightweight profile with person_id and secondary skills.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower($skill) IN [s IN p.secondary_skills | toLower(s)]
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.headline as headline,
            p.secondary_skills as secondary_skills
        ORDER BY name
        """
        return self.db.execute_query(query, params={"skill": skill})


    def find_people_by_current_company(self, company_name):
        """
        Finds people who CURRENTLY work at a specific company.
        Searches the current_company property on Person nodes (fast, direct property match).
        Use this when you need current employees only.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower(p.current_company) CONTAINS toLower($company_name)
        RETURN 
            p.person_id as person_id,
            p.name as name, 
            p.current_company as current_company,
            p.current_title as current_title,
            p.current_location as location
        ORDER BY name
        """
        return self.db.execute_query(query, params={"company_name": company_name})


    def find_people_by_company_history(self, company_name):
        """
        Finds all people who have worked at a specific company (current OR past employees).
        Uses split relationships: CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT.
        Use this when you want to find anyone who has EVER worked at a company.
        For current employees only, use find_people_by_current_company instead.
        Returns lightweight profile with person_id and employment details.
        """
        query = """
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE toLower(c.name) CONTAINS toLower($company_name)
        RETURN DISTINCT 
            p.person_id as person_id,
            p.name as name,
            c.name as company_name,
            r.role as title,
            r.is_current as is_current
        ORDER BY r.is_current DESC, name
        """
        return self.db.execute_query(query, params={"company_name": company_name})


    def find_people_by_institution(self, institution_name):
        """
        Finds all people who studied at a specific institution.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p:Person)-[:STUDIED_AT]->(i:Institution)
        WHERE toLower(i.name) CONTAINS toLower($institution_name)
        RETURN DISTINCT 
            p.person_id as person_id,
            p.name as name,
            p.current_company as current_company,
            p.current_location as location,
            i.name as institution_name
        ORDER BY name
        """
        return self.db.execute_query(query, params={"institution_name": institution_name})


    def find_people_by_location(self, location):
        """
        Finds all people in a specific location.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p:Person)
        WHERE toLower(p.current_location) CONTAINS toLower($location)
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.current_location as location,
            p.current_company as current_company
        ORDER BY name
        """
        return self.db.execute_query(query, params={"location": location})


    def find_people_by_experience_level(self, min_months=None, max_months=None):
        """
        Finds people based on their total experience in months.
        Returns lightweight profile with person_id.
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
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.total_experience_months as experience_months,
            p.current_company as current_company,
            p.current_title as current_title
        ORDER BY p.total_experience_months DESC
        """
        return self.db.execute_query(query, params=params)


    def get_person_job_descriptions(self, person_id=None, person_name=None):
        """
        Gets all job descriptions for a person with company and role details.
        Job descriptions are stored on relationship properties.
        This is the foundation for technical skill discovery, behavioral analysis, and career progression.
        Returns person_id and full job history with descriptions.
        """
        if person_id:
            match_clause = "MATCH (p:Person {person_id: $person_id})"
            params = {"person_id": person_id}
        elif person_name:
            match_clause = "MATCH (p:Person) WHERE toLower(p.name) CONTAINS toLower($person_name)"
            params = {"person_name": person_name}
        else:
            return {"error": "Must provide either person_id or person_name"}
        
        query = f"""
        {match_clause}
        MATCH (p)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        RETURN 
            p.person_id as person_id,
            p.name as person_name,
            c.name as company_name,
            r.role as job_title,
            r.description as job_description,
            r.duration_months as duration_months
        ORDER BY r.start_date DESC
        """
        return self.db.execute_query(query, params=params)

    
    def search_job_descriptions_by_keywords(self, keywords, match_type="any"):
        """
        Search for people based on keywords in their job descriptions.
        Job descriptions are stored on relationships.
        Useful for finding technical skills, behavioral patterns, or specific experience.
        Returns person_id and matching job details.
        
        Args:
            keywords: List of keywords to search for in job descriptions
            match_type: "any" to match any keyword, "all" to match all keywords
        """
        if match_type == "all":
            # All keywords must be present in job description
            conditions = [f"toLower(r.description) CONTAINS toLower('{keyword}')" for keyword in keywords]
            where_clause = " AND ".join(conditions)
        else:
            # Any keyword can be present
            conditions = [f"toLower(r.description) CONTAINS toLower('{keyword}')" for keyword in keywords]
            where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN DISTINCT 
            p.person_id as person_id,
            p.name as person_name,
            c.name as company_name, 
            r.role as job_title,
            r.description as job_description
        ORDER BY p.name
        """
        return self.db.execute_query(query)

    
    def find_domain_experts(self, domain_keywords):
        """
        Find people with deep domain expertise based on job description analysis.
        Returns person_id and expertise indicators.
        
        Args:
            domain_keywords: List of domain-specific terms (e.g., ["fintech", "healthcare", "e-commerce"])
        """
        conditions = [f"toLower(r.description) CONTAINS toLower('{keyword}')" for keyword in domain_keywords]
        where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        WITH p, count(r) as domain_jobs, collect(DISTINCT c.name) as companies,
             collect(DISTINCT r.role) as roles
        WHERE domain_jobs >= 2  // At least 2 jobs in the domain
        RETURN 
            p.person_id as person_id,
            p.name as person_name,
            domain_jobs,
            p.current_company as current_company,
            p.current_title as current_title
        ORDER BY domain_jobs DESC
        """
        return self.db.execute_query(query)

    
