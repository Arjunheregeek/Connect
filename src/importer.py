# --- src/importer.py ---
import pandas as pd
import json
import ast
from datetime import datetime
from typing import List, Dict, Any

class KnowledgeGraphImporter:
    """
    Imports LinkedIn profile data from CSV into Neo4j knowledge graph.
    Follows the optimized structure with 5 node types and 7 relationship types.
    """
    def __init__(self, db_driver, csv_path):
        """
        Initializes the importer with a database driver and the path to the CSV.
        """
        self.db = db_driver
        self.csv_path = csv_path
        self.stats = {
            'persons': 0,
            'companies': 0,
            'institutions': 0,
            'currently_works_at': 0,
            'previously_worked_at': 0,
            'studied_at': 0,
            'errors': 0
        }

    def setup_constraints(self):
        """
        Sets up unique constraints on node properties in the database to ensure
        data integrity and improve query performance. This is idempotent.
        """
        print("\n🔧 Setting up database constraints and indexes...")
        
        constraints = [
            # Person constraints
            "CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE",
            "CREATE CONSTRAINT person_email_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.email IS UNIQUE",
            "CREATE CONSTRAINT person_linkedin_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.linkedin_profile IS UNIQUE",
            
            # Company constraints
            "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
            
            # Institution constraints
            "CREATE CONSTRAINT institution_name_unique IF NOT EXISTS FOR (i:Institution) REQUIRE i.name IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                self.db.execute_query(constraint)
                print(f"  ✓ {constraint.split('FOR')[0].strip()}")
            except Exception as e:
                print(f"  ⚠️  Constraint might already exist: {e}")
        
        print("\n🔧 Creating indexes...")
        indexes = [
            "CREATE INDEX person_name_idx IF NOT EXISTS FOR (p:Person) ON (p.name)",
            "CREATE INDEX person_seniority_idx IF NOT EXISTS FOR (p:Person) ON (p.seniority_level)",
            "CREATE INDEX person_expertise_idx IF NOT EXISTS FOR (p:Person) ON (p.primary_expertise)",
            "CREATE INDEX person_industry_idx IF NOT EXISTS FOR (p:Person) ON (p.industry)",
        ]
        
        for index in indexes:
            try:
                self.db.execute_query(index)
                print(f"  ✓ {index.split('FOR')[0].strip()}")
            except Exception as e:
                print(f"  ⚠️  Index might already exist: {e}")
        
        print("✅ Constraints and indexes are set.\n")

    def import_data(self):
        """
        Loads the CSV data and iterates through each row to import it.
        """
        try:
            print(f"📂 Loading data from {self.csv_path}...")
            df = pd.read_csv(self.csv_path)
            # Replace pandas NaN/NaT with None for Neo4j compatibility
            df = df.where(pd.notna(df), None)
            print(f"✅ Loaded {len(df)} records\n")
            
            print("=" * 80)
            print("Starting import process...")
            print("=" * 80 + "\n")
            
            for index, row in df.iterrows():
                try:
                    self._import_person(row)
                    print(f"✓ Processed {index + 1}/{len(df)}: {row.get('name', 'Unknown')}")
                except Exception as e:
                    self.stats['errors'] += 1
                    print(f"  ❌ Error processing row {index + 1} ({row.get('name', 'Unknown')}): {e}")
            
            self._print_statistics()

        except FileNotFoundError:
            print(f"❌ Error: The file was not found at '{self.csv_path}'")
            return
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return

    def _parse_list_string(self, list_str: str) -> List[str]:
        """
        Safely parse a string representation of a list into an actual list.
        Handles formats like "['item1', 'item2']" or None.
        """
        if not list_str or list_str is None:
            return []
        
        try:
            # Try ast.literal_eval first (safest)
            parsed = ast.literal_eval(list_str)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
            return []
        except:
            try:
                # Fallback to json.loads
                parsed = json.loads(list_str)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if item]
                return []
            except:
                return []

    def _parse_json_string(self, json_str: str) -> List[Dict]:
        """
        Safely parse a JSON string into a list of dictionaries.
        """
        if not json_str or json_str is None:
            return []
        
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return parsed
            return []
        except:
            return []

    def _import_person(self, row):
        """
        Imports a single person's data - all properties stored on Person node.
        Creates Company and Institution nodes only for relationships.
        """
        person_id = int(row['person_id']) if row.get('person_id') else None
        if not person_id:
            return  # Skip if there is no person ID

        # --- Step 1: Create Person Node with ALL properties ---
        self._create_person_node(row, person_id)
        
        # --- Step 2: Create Work Experience Relationships (Person -> Company) ---
        self._create_work_relationships(person_id, row)
        
        # --- Step 3: Create Education Relationships (Person -> Institution) ---
        self._create_education_relationships(person_id, row)

    def _create_person_node(self, row, person_id):
        """Create the Person node with ALL properties including skills as arrays."""
        person_query = """
        MERGE (p:Person {person_id: $person_id})
        SET 
            p.name = $name,
            p.linkedin_profile = $linkedin_profile,
            p.email = $email,
            p.phone = $phone,
            p.current_location = $current_location,
            p.headline = $headline,
            p.summary = $summary,
            p.followers_count = $followers_count,
            p.trustworthiness_score = $trustworthiness_score,
            p.perceived_expertise_level = $perceived_expertise_level,
            p.competence_score = $competence_score,
            p.current_title = $current_title,
            p.current_company = $current_company,
            p.industry = $industry,
            p.seniority_level = $seniority_level,
            p.years_of_experience = $years_of_experience,
            p.employment_type = $employment_type,
            p.professional_status = $professional_status,
            p.primary_expertise = $primary_expertise,
            p.total_experience_months = $total_experience_months,
            p.technical_skills = $technical_skills,
            p.secondary_skills = $secondary_skills,
            p.domain_knowledge = $domain_knowledge,
            p.degrees = $degrees,
            p.current_goals = $current_goals,
            p.current_challenges = $current_challenges,
            p.resources_needed = $resources_needed,
            p.availability_hiring = $availability_hiring,
            p.availability_roles = $availability_roles,
            p.availability_cofounder = $availability_cofounder,
            p.availability_advisory = $availability_advisory,
            p.updated_at = datetime()
        """
        
        person_params = {
            "person_id": person_id,
            "name": row.get('name'),
            "linkedin_profile": row.get('linkedin_profile'),
            "email": row.get('email'),
            "phone": str(row.get('phone')) if row.get('phone') else None,
            "current_location": row.get('current_location'),
            "headline": row.get('headline'),
            "summary": row.get('summary'),
            "followers_count": float(row.get('followers_count')) if row.get('followers_count') else None,
            "trustworthiness_score": int(row.get('trustworthiness_score')) if row.get('trustworthiness_score') else None,
            "perceived_expertise_level": int(row.get('perceived_expertise_level')) if row.get('perceived_expertise_level') else None,
            "competence_score": int(row.get('competence_score')) if row.get('competence_score') else None,
            "current_title": row.get('current_title'),
            "current_company": row.get('current_company'),
            "industry": row.get('industry'),
            "seniority_level": row.get('seniority_level'),
            "years_of_experience": float(row.get('years_of_experience')) if row.get('years_of_experience') else None,
            "employment_type": row.get('employment_type'),
            "professional_status": row.get('professional_status'),
            "primary_expertise": row.get('primary_expertise'),
            "total_experience_months": float(row.get('total_experience_months')) if row.get('total_experience_months') else None,
            "technical_skills": self._parse_list_string(row.get('technical_skills')),
            "secondary_skills": self._parse_list_string(row.get('secondary_skills')),
            "domain_knowledge": self._parse_list_string(row.get('domain_knowledge')),
            "degrees": self._parse_list_string(row.get('degrees')),
            "current_goals": row.get('current_goals'),
            "current_challenges": row.get('current_challenges'),
            "resources_needed": row.get('resources_needed'),
            "availability_hiring": row.get('availability_hiring'),
            "availability_roles": row.get('availability_roles'),
            "availability_cofounder": row.get('availability_cofounder'),
            "availability_advisory": row.get('availability_advisory'),
        }
        
        self.db.execute_query(person_query, person_params)
        self.stats['persons'] += 1

    def _create_work_relationships(self, person_id, row):
        """Create Company nodes and work relationships (CURRENTLY_WORKS_AT, PREVIOUSLY_WORKED_AT)."""
        experience_history = self._parse_json_string(row.get('experience_history'))
        
        if not experience_history:
            return
        
        for job in experience_history:
            company_name = job.get('company_name')
            if not company_name:
                continue
            
            # Determine if this is current or previous work
            end_date = job.get('end_date')
            is_current = end_date is None or end_date == 'null' or end_date == ''
            
            relationship_type = 'CURRENTLY_WORKS_AT' if is_current else 'PREVIOUSLY_WORKED_AT'
            
            work_query = f"""
            MATCH (p:Person {{person_id: $person_id}})
            MERGE (c:Company {{name: $company_name}})
            ON CREATE SET c.created_at = datetime()
            MERGE (p)-[r:{relationship_type}]->(c)
            SET r.role = $title,
                r.start_date = $start_date,
                r.end_date = $end_date,
                r.duration_months = $duration_months,
                r.description = $description,
                r.location = $location,
                r.is_current = $is_current,
                r.created_at = datetime()
            """
            
            work_params = {
                "person_id": person_id,
                "company_name": company_name,
                "title": job.get('title'),
                "start_date": job.get('start_date'),
                "end_date": end_date,
                "duration_months": job.get('duration_months'),
                "description": job.get('description'),
                "location": job.get('location'),
                "is_current": is_current
            }
            
            self.db.execute_query(work_query, work_params)
            
            if is_current:
                self.stats['currently_works_at'] += 1
            else:
                self.stats['previously_worked_at'] += 1

    def _create_education_relationships(self, person_id, row):
        """Create Institution nodes and STUDIED_AT relationships."""
        education_history = self._parse_json_string(row.get('education_history'))
        
        if not education_history:
            return
        
        for edu in education_history:
            institution_name = edu.get('institution_name')
            if not institution_name:
                continue
            
            education_query = """
            MATCH (p:Person {person_id: $person_id})
            MERGE (i:Institution {name: $institution_name})
            ON CREATE SET i.created_at = datetime()
            MERGE (p)-[r:STUDIED_AT]->(i)
            SET r.degree = $degree,
                r.start_year = $start_year,
                r.end_year = $end_year,
                r.created_at = datetime()
            """
            
            education_params = {
                "person_id": person_id,
                "institution_name": institution_name,
                "degree": edu.get('degree'),
                "start_year": edu.get('start_year'),
                "end_year": edu.get('end_year')
            }
            
            self.db.execute_query(education_query, education_params)
            self.stats['studied_at'] += 1

    def _print_statistics(self):
        """Print import statistics."""
        print("\n" + "=" * 80)
        print("📊 IMPORT STATISTICS")
        print("=" * 80)
        print(f"\n✅ Nodes Created:")
        print(f"   • Person nodes:      {self.stats['persons']}")
        print(f"   • Company nodes:     ~{self.stats['currently_works_at'] + self.stats['previously_worked_at']} (estimated)")
        print(f"   • Institution nodes: ~{self.stats['studied_at']} (estimated)")
        
        print(f"\n🔗 Relationships Created:")
        print(f"   • CURRENTLY_WORKS_AT:    {self.stats['currently_works_at']}")
        print(f"   • PREVIOUSLY_WORKED_AT:  {self.stats['previously_worked_at']}")
        print(f"   • STUDIED_AT:            {self.stats['studied_at']}")
        
        total_relationships = (
            self.stats['currently_works_at'] +
            self.stats['previously_worked_at'] +
            self.stats['studied_at']
        )
        print(f"\n   📈 Total Relationships:  {total_relationships}")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  Errors encountered:   {self.stats['errors']}")
        
        print("\n" + "=" * 80)
        print("✅ Import completed successfully!")
        print("=" * 80 + "\n")

