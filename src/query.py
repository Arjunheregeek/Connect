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
        Returns the complete profile for a person including ALL 35 properties,
        work history with job descriptions, and education history.
        This is the heavyweight query that returns everything.
        
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
            description: work.description,
            start_date: work.start_date,
            end_date: work.end_date,
            duration_months: work.duration_months,
            location: work.location,
            is_current: work.is_current
        }}) as work_history
        
        // Get education history
        OPTIONAL MATCH (p)-[edu:STUDIED_AT]->(i:Institution)
        WITH p, work_history, collect(DISTINCT {{
            institution: i.name,
            degree: edu.degree,
            start_year: edu.start_year,
            end_year: edu.end_year
        }}) as education_history
        
        // Return ALL 35 properties plus relationships
        RETURN 
            p.person_id as person_id,
            p.name as name,
            p.headline as headline,
            p.summary as summary,
            p.email as email,
            p.phone as phone,
            p.linkedin_profile as linkedin_profile,
            p.location as location,
            p.current_company as current_company,
            p.current_title as current_title,
            p.total_experience_months as total_experience_months,
            p.technical_skills as technical_skills,
            p.secondary_skills as secondary_skills,
            p.domain_knowledge as domain_knowledge,
            p.certifications as certifications,
            p.languages as languages,
            p.industry as industry,
            p.seniority_level as seniority_level,
            p.function as function,
            p.company_size_preference as company_size_preference,
            p.willing_to_relocate as willing_to_relocate,
            p.remote_work_preference as remote_work_preference,
            p.expected_salary_min as expected_salary_min,
            p.expected_salary_max as expected_salary_max,
            p.currency as currency,
            p.notice_period_days as notice_period_days,
            p.actively_looking as actively_looking,
            p.open_to_opportunities as open_to_opportunities,
            p.preferred_locations as preferred_locations,
            p.work_authorization as work_authorization,
            p.visa_sponsorship_needed as visa_sponsorship_needed,
            p.github_profile as github_profile,
            p.portfolio_url as portfolio_url,
            p.twitter_handle as twitter_handle,
            p.created_at as created_at,
            p.updated_at as updated_at,
            work_history,
            education_history
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
            p.summary as summary,
            p.linkedin_profile as linkedin_profile,
            p.email as email,
            p.location as location,
            p.current_company as current_company,
            p.current_title as current_title,
            p.total_experience_months as total_experience_months
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
            p.headline as headline,
            p.summary as summary,
            p.current_company as current_company,
            p.current_title as current_title,
            p.technical_skills as technical_skills,
            p.secondary_skills as secondary_skills,
            p.domain_knowledge as domain_knowledge,
            p.total_experience_months as total_experience_months
        ORDER BY name
        """
        return self.db.execute_query(query, params={"skill": skill})

    def find_people_by_company(self, company_name):
        """
        Finds all people who have worked at a specific company (current or past).
        Uses split relationships: CURRENTLY_WORKS_AT and PREVIOUSLY_WORKED_AT.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE toLower(c.name) CONTAINS toLower($company_name)
        RETURN DISTINCT 
            p.person_id as person_id,
            p.name as name, 
            p.headline as headline,
            p.summary as summary,
            c.name as company_name,
            r.role as title,
            r.is_current as is_current,
            r.start_date as start_date,
            r.end_date as end_date,
            p.location as location
        ORDER BY r.is_current DESC, name
        """
        return self.db.execute_query(query, params={"company_name": company_name})
    
    def find_colleagues_at_company(self, person_id, company_name):
        """
        Finds who a specific person worked with at a given company.
        Uses split relationships for accurate colleague matching.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p1:Person {id: $person_id})-[:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
              <-[:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]-(p2:Person)
        WHERE toLower(c.name) CONTAINS toLower($company_name) AND p1 <> p2
        RETURN 
            p2.id as person_id,
            p2.name as colleague_name, 
            p2.headline as colleague_headline,
            p2.summary as colleague_summary,
            p2.current_company as current_company,
            p2.current_title as current_title,
            p2.email as email,
            p2.linkedin_profile as linkedin_profile,
            c.name as company_name
        ORDER BY colleague_name
        """
        return self.db.execute_query(query, params={"person_id": person_id, "company_name": company_name})

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
            p.headline as headline,
            p.summary as summary,
            p.current_company as current_company,
            p.current_title as current_title,
            p.location as location,
            p.email as email,
            p.linkedin_profile as linkedin_profile,
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
        WHERE toLower(p.location) CONTAINS toLower($location)
        RETURN 
            p.person_id as person_id,
            p.name as name, 
            p.headline as headline, 
            p.summary as summary,
            p.location as location,
            p.current_company as current_company,
            p.current_title as current_title,
            p.email as email,
            p.linkedin_profile as linkedin_profile,
            p.total_experience_months as total_experience_months
        ORDER BY name
        """
        return self.db.execute_query(query, params={"location": location})

    def get_person_skills(self, person_id=None, person_name=None):
        """
        Gets all skills for a specific person from their skill arrays.
        Skills are stored directly on Person nodes as arrays.
        Returns person_id and all skill categories.
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
        RETURN 
            p.person_id as person_id,
            p.name as person_name, 
            p.headline as headline,
            p.summary as summary,
            p.technical_skills as technical_skills,
            p.secondary_skills as secondary_skills,
            p.domain_knowledge as domain_knowledge
        """
        return self.db.execute_query(query, params=params)

    def find_people_with_multiple_skills(self, skills_list, match_type="any"):
        """
        Finds people who have multiple skills from their skill arrays.
        
        Args:
            skills_list: List of skills to search for
            match_type: "any" to match any skill, "all" to match all skills
        Returns lightweight profile with person_id and matched skills.
        """
        # Convert skills to lowercase for case-insensitive matching
        skills_lower = [skill.lower() for skill in skills_list]
        
        if match_type == "all":
            # Find people who have ALL the specified skills across all skill arrays
            query = """
            MATCH (p:Person)
            WITH p, 
                 [s IN p.technical_skills | toLower(s)] + 
                 [s IN p.secondary_skills | toLower(s)] + 
                 [s IN p.domain_knowledge | toLower(s)] as all_skills
            WITH p, all_skills, $skills_list as required_skills
            WHERE ALL(skill IN required_skills WHERE skill IN all_skills)
            RETURN 
                p.person_id as person_id,
                p.name as name, 
                p.headline as headline,
                p.summary as summary,
                p.technical_skills as technical_skills,
                p.secondary_skills as secondary_skills,
                p.domain_knowledge as domain_knowledge,
                p.current_company as current_company,
                p.current_title as current_title,
                p.total_experience_months as total_experience_months
            ORDER BY name
            """
            return self.db.execute_query(query, params={"skills_list": skills_lower})
        else:
            # Find people who have ANY of the specified skills
            query = """
            MATCH (p:Person)
            WITH p, 
                 [s IN p.technical_skills | toLower(s)] + 
                 [s IN p.secondary_skills | toLower(s)] + 
                 [s IN p.domain_knowledge | toLower(s)] as all_skills
            WITH p, all_skills, $skills_list as search_skills
            WHERE ANY(skill IN search_skills WHERE skill IN all_skills)
            RETURN 
                p.person_id as person_id,
                p.name as name, 
                p.headline as headline,
                p.summary as summary,
                p.technical_skills as technical_skills,
                p.secondary_skills as secondary_skills,
                p.domain_knowledge as domain_knowledge,
                p.current_company as current_company,
                p.current_title as current_title,
                p.total_experience_months as total_experience_months
            ORDER BY name
            """
            return self.db.execute_query(query, params={"skills_list": skills_lower})

    def get_person_colleagues(self, person_id=None, person_name=None):
        """
        Gets all colleagues of a person across all companies they worked at.
        Uses split relationships for accurate colleague matching.
        Returns lightweight profile with person_id for each colleague.
        """
        if person_id:
            match_clause = "MATCH (p1:Person {id: $person_id})"
            params = {"person_id": person_id}
        elif person_name:
            match_clause = "MATCH (p1:Person) WHERE toLower(p1.name) CONTAINS toLower($person_name)"
            params = {"person_name": person_name}
        else:
            return {"error": "Must provide either person_id or person_name"}
        
        query = f"""
        {match_clause}
        MATCH (p1)-[:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
              <-[:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]-(p2:Person)
        WHERE p1 <> p2
        RETURN 
            p2.id as person_id,
            p2.name as colleague_name, 
            p2.headline as colleague_headline,
            p2.summary as colleague_summary,
            p2.current_company as current_company,
            p2.current_title as current_title,
            p2.email as email,
            p2.linkedin_profile as linkedin_profile,
            c.name as company_name
        ORDER BY company_name, colleague_name
        """
        return self.db.execute_query(query, params=params)

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
            p.headline as headline, 
            p.summary as summary,
            p.total_experience_months as experience_months,
            p.current_company as current_company,
            p.current_title as current_title,
            p.location as location,
            p.email as email,
            p.linkedin_profile as linkedin_profile
        ORDER BY p.total_experience_months DESC
        """
        return self.db.execute_query(query, params=params)

    def get_company_employees(self, company_name):
        """
        Gets all employees (past and present) of a specific company.
        Uses split relationships to show current vs past employees.
        Returns lightweight profile with person_id.
        """
        query = """
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE toLower(c.name) CONTAINS toLower($company_name)
        RETURN 
            p.person_id as person_id,
            p.name as name, 
            p.headline as headline,
            p.summary as summary,
            c.name as company_name,
            r.role as title,
            r.is_current as is_current,
            r.start_date as start_date,
            r.end_date as end_date,
            p.location as location
        ORDER BY r.is_current DESC, name
        """
        return self.db.execute_query(query, params={"company_name": company_name})

    def get_skill_popularity(self, limit=20):
        """
        Gets the most popular skills by counting how many people have each skill.
        Skills are stored as arrays, so we need to unwind and count them.
        """
        query = """
        MATCH (p:Person)
        WITH p.technical_skills + p.secondary_skills + p.domain_knowledge as all_skills
        UNWIND all_skills as skill
        WITH toLower(skill) as skill_name
        WHERE skill_name IS NOT NULL AND skill_name <> ''
        RETURN skill_name, count(*) as person_count
        ORDER BY person_count DESC
        LIMIT $limit
        """
        return self.db.execute_query(query, params={"limit": limit})

    def get_person_details(self, person_id=None, person_name=None):
        """
        Gets comprehensive details about a person including skills, companies, and education.
        This is similar to get_person_complete_profile but returns a summary view.
        Returns person_id and aggregated information.
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
        OPTIONAL MATCH (p)-[:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        OPTIONAL MATCH (p)-[:STUDIED_AT]->(i:Institution)
        RETURN 
            p.person_id as person_id,
            p.name as name, 
            p.headline as headline, 
            p.summary as summary,
            p.location as location,
            p.linkedin_profile as linkedin_profile, 
            p.email as email,
            p.total_experience_months as experience_months,
            p.technical_skills as technical_skills,
            p.secondary_skills as secondary_skills,
            p.domain_knowledge as domain_knowledge,
            collect(DISTINCT c.name) as companies,
            collect(DISTINCT i.name) as institutions
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
            p.headline as headline,
            p.summary as summary,
            c.name as company_name,
            r.role as job_title,
            r.description as job_description,
            r.start_date as start_date,
            r.end_date as end_date,
            r.duration_months as duration_months,
            r.location as job_location,
            r.is_current as is_current
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
            p.headline as headline,
            p.summary as summary,
            c.name as company_name, 
            r.role as job_title,
            r.description as job_description,
            r.is_current as is_current,
            p.email as email,
            p.location as location
        ORDER BY p.name
        """
        return self.db.execute_query(query)
    
    def find_technical_skills_in_descriptions(self, tech_keywords):
        """
        Find people who mention specific technical skills in their job descriptions.
        Goes beyond structured skills to find contextual technical mentions.
        Returns person_id and matching job details.
        
        Args:
            tech_keywords: List of technical terms to search for (e.g., ["python", "kubernetes", "machine learning"])
        """
        # Create case-insensitive search conditions
        conditions = [f"toLower(r.description) CONTAINS toLower('{keyword}')" for keyword in tech_keywords]
        where_clause = " OR ".join(conditions)
        
        query = f"""
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN 
            p.person_id as person_id,
            p.name as person_name, 
            p.headline as headline,
            p.summary as summary,
            c.name as company_name, 
            r.role as job_title,
            r.description as job_description,
            r.start_date as start_date, 
            r.end_date as end_date,
            r.is_current as is_current,
            p.location as location
        ORDER BY r.start_date DESC
        """
        return self.db.execute_query(query)
    
    def find_leadership_indicators(self):
        """
        Find people with leadership indicators in their job descriptions.
        Looks for management, team lead, and leadership-related keywords.
        Returns person_id and job details showing leadership experience.
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
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN 
            p.person_id as person_id,
            p.name as person_name, 
            p.headline as headline,
            p.summary as summary,
            c.name as company_name, 
            r.role as job_title,
            r.description as job_description,
            r.duration_months as duration_months,
            r.is_current as is_current,
            p.location as location
        ORDER BY r.duration_months DESC
        """
        return self.db.execute_query(query)
    
    def find_achievement_patterns(self):
        """
        Find people with quantifiable achievements in their job descriptions.
        Looks for metrics, improvements, and measurable impact.
        Returns person_id and job details highlighting achievements.
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
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE r.description IS NOT NULL AND ({where_clause})
        RETURN 
            p.person_id as person_id,
            p.name as person_name, 
            p.headline as headline,
            p.summary as summary,
            c.name as company_name, 
            r.role as job_title,
            r.description as job_description,
            r.start_date as start_date, 
            r.end_date as end_date,
            r.is_current as is_current,
            p.location as location
        ORDER BY p.name
        """
        return self.db.execute_query(query)
    
    def analyze_career_progression(self, person_id=None, person_name=None):
        """
        Analyze a person's career progression by examining job titles and descriptions over time.
        Shows how their roles, responsibilities, and seniority evolved.
        Returns person_id and chronological job history.
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
            p.headline as headline,
            p.summary as summary,
            c.name as company_name,
            r.role as job_title,
            r.description as job_description,
            r.start_date as start_date,
            r.end_date as end_date,
            r.duration_months as duration_months,
            r.location as job_location,
            r.is_current as is_current
        ORDER BY r.start_date ASC
        """
        return self.db.execute_query(query, params=params)
    
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
            p.headline as headline,
            p.summary as summary,
            domain_jobs, 
            companies, 
            roles,
            p.total_experience_months as total_experience,
            p.location as location,
            p.email as email
        ORDER BY domain_jobs DESC, p.total_experience_months DESC
        """
        return self.db.execute_query(query)
    
    def find_similar_career_paths(self, reference_person_id=None, reference_person_name=None, similarity_threshold=2):
        """
        Find people with similar career paths to a reference person.
        Compares job titles, companies, and progression patterns.
        Returns person_id and similarity metrics.
        
        Args:
            reference_person_id: The person ID to compare against (preferred)
            reference_person_name: The person name to compare against (alternative)
            similarity_threshold: Minimum number of similar elements (companies/roles)
        """
        if reference_person_id:
            ref_match = "MATCH (ref:Person {id: $reference_id})"
            params = {"reference_id": reference_person_id, "threshold": similarity_threshold}
        elif reference_person_name:
            ref_match = "MATCH (ref:Person) WHERE toLower(ref.name) CONTAINS toLower($reference_name)"
            params = {"reference_name": reference_person_name, "threshold": similarity_threshold}
        else:
            return {"error": "Must provide either reference_person_id or reference_person_name"}
        
        query = f"""
        // Get reference person's career data
        {ref_match}
        MATCH (ref)-[ref_r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(ref_c:Company)
        WITH ref, collect(DISTINCT ref_c.name) as ref_companies, 
             collect(DISTINCT toLower(ref_r.role)) as ref_titles
        
        // Find people with overlapping companies or similar titles
        MATCH (p:Person)-[r:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c:Company)
        WHERE p <> ref
        WITH ref, ref_companies, ref_titles, p,
             collect(DISTINCT c.name) as person_companies,
             collect(DISTINCT toLower(r.role)) as person_titles
        
        // Calculate similarity
        WITH ref, p, ref_companies, ref_titles, person_companies, person_titles,
             [x IN ref_companies WHERE x IN person_companies] as common_companies,
             [x IN ref_titles WHERE x IN person_titles] as common_titles
        
        WHERE size(common_companies) + size(common_titles) >= $threshold
        
        RETURN 
            p.person_id as person_id,
            p.name as similar_person, 
            p.headline as headline,
            p.summary as summary,
            common_companies, 
            common_titles,
            size(common_companies) + size(common_titles) as similarity_score,
            p.location as location,
            p.email as email,
            p.current_company as current_company
        ORDER BY similarity_score DESC
        """
        return self.db.execute_query(query, params=params)
    
    def find_role_transition_patterns(self, from_role_keywords, to_role_keywords):
        """
        Find people who transitioned from one type of role to another.
        Useful for understanding career pivot patterns.
        Returns person_id and transition details.
        
        Args:
            from_role_keywords: Keywords for the starting role type
            to_role_keywords: Keywords for the target role type
        """
        from_conditions = [f"toLower(r1.role) CONTAINS '{keyword}'" for keyword in from_role_keywords]
        to_conditions = [f"toLower(r2.role) CONTAINS '{keyword}'" for keyword in to_role_keywords] 
        
        from_clause = " OR ".join(from_conditions)
        to_clause = " OR ".join(to_conditions)
        
        query = f"""
        MATCH (p:Person)-[r1:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c1:Company)
        MATCH (p)-[r2:CURRENTLY_WORKS_AT|PREVIOUSLY_WORKED_AT]->(c2:Company)
        WHERE r1.start_date < r2.start_date
          AND ({from_clause})
          AND ({to_clause})
        RETURN 
            p.person_id as person_id,
            p.name as person_name, 
            p.headline as headline,
            p.summary as summary,
            c1.name as from_company, 
            r1.role as from_role, 
            r1.start_date as from_start,
            c2.name as to_company, 
            r2.role as to_role, 
            r2.start_date as to_start,
            r1.description as from_description, 
            r2.description as to_description,
            p.location as location,
            p.email as email
        ORDER BY r2.start_date DESC
        """
        return self.db.execute_query(query)
