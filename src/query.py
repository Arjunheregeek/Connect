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
