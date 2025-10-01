# --- src/importer.py ---
import pandas as pd
import json

class KnowledgeGraphImporter:
    """
    Reads structured data from a CSV file and imports it into a Neo4j
    knowledge graph.
    """
    def __init__(self, db_driver, csv_path):
        """
        Initializes the importer with a database driver and the path to the CSV.
        """
        self.db = db_driver
        self.csv_path = csv_path

    def setup_constraints(self):
        """
        Sets up unique constraints on node properties in the database to ensure
        data integrity and improve query performance. This is idempotent.
        """
        print("Setting up database constraints...")
        # Using execute_query from the GraphDB class
        self.db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE")
        self.db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.url IS UNIQUE")
        self.db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Institution) REQUIRE i.url IS UNIQUE")
        self.db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")
        print("Constraints are set.")

    def import_data(self):
        """
        Loads the CSV data and iterates through each row to import it.
        """
        try:
            df = pd.read_csv(self.csv_path)
            # Replace pandas NaN/NaT with None for Neo4j compatibility
            df = df.where(pd.notna(df), None)
            print(f"Loaded {len(df)} records from {self.csv_path}")
            
            for index, row in df.iterrows():
                try:
                    self._import_person(row)
                    print(f"Processing record {index + 1}/{len(df)}: {row['name']}")
                except Exception as e:
                    print(f"  - ❗️ Error processing row {index + 1} ({row['name']}): {e}")

        except FileNotFoundError:
            print(f"❌ Error: The file was not found at '{self.csv_path}'")
            return

    def _import_person(self, row):
        """
        Imports a single person's data, including their skills, education,
        and work experience, into the graph.
        """
        person_id = int(row['id']) if row['id'] else None
        if not person_id:
            return # Skip if there is no person ID

        # --- Create Person Node ---
        person_query = """
        MERGE (p:Person {id: $id})
        SET p.name = $name, p.linkedin_profile = $profile, p.email = $email,
            p.phone = $phone, p.location = $location, p.headline = $headline,
            p.summary = $summary, p.followers_count = $followers,
            p.total_experience_months = $total_exp
        """
        person_params = {
            "id": person_id, "name": row['name'], "profile": row['linkedin_profile'],
            "email": row['email'], "phone": str(row['phone']), "location": row['location'],
            "headline": row['headline'], "summary": row['summary'],
            "followers": row['followers_count'], "total_exp": row['total_experience_months']
        }
        self.db.execute_query(person_query, person_params)

        # --- Create Skills and Relationships ---
        if row['skills']:
            skills = json.loads(row['skills'])
            skills_query = """
            MATCH (p:Person {id: $person_id})
            UNWIND $skills as skill_name
            MERGE (s:Skill {name: toLower(skill_name)})
            MERGE (p)-[:HAS_SKILL]->(s)
            """
            self.db.execute_query(skills_query, params={"person_id": person_id, "skills": skills})
        
        # --- Create Experience and Relationships ---
        if row['experience_history']:
            jobs = json.loads(row['experience_history'])
            
            # **THE FIX IS HERE:** We filter out jobs that don't have a URL before sending to the DB.
            valid_jobs = [job for job in jobs if job.get('company_linkedin_url')]

            if valid_jobs:
                experience_query = """
                MATCH (p:Person {id: $person_id})
                UNWIND $jobs as job
                MERGE (c:Company {url: job.company_linkedin_url})
                SET c.name = job.company_name
                CREATE (p)-[r:WORKS_AT]->(c)
                SET r.title = job.title, r.start_date = job.start_date, r.end_date = job.end_date,
                    r.duration_months = job.duration_months, r.description = job.description,
                    r.location = job.location
                """
                self.db.execute_query(experience_query, params={"person_id": person_id, "jobs": valid_jobs})

        # --- Create Education and Relationships ---
        if row['education_history']:
            educations = json.loads(row['education_history'])

            # Add a similar filter for education to be safe
            valid_educations = [edu for edu in educations if edu.get('institution_url')]

            if valid_educations:
                education_query = """
                MATCH (p:Person {id: $person_id})
                UNWIND $educations as edu
                MERGE (i:Institution {url: edu.institution_url})
                SET i.name = edu.institution_name
                CREATE (p)-[r:STUDIED_AT]->(i)
                SET r.degree = edu.degree, r.start_year = edu.start_year, r.end_year = edu.end_year
                """
                self.db.execute_query(education_query, params={"person_id": person_id, "educations": valid_educations})

