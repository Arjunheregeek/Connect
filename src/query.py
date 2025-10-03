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
