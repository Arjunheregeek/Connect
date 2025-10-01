# --- main.py ---
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.graph_db import GraphDB
from src.importer import KnowledgeGraphImporter

def main():
    load_dotenv()
    
    uri = "neo4j+s://4bb44263.databases.neo4j.io"
    user = os.getenv("NEO_USERNAME")
    password = os.getenv("NEO_PASSWORD")
    
    if not user or not password:
        print("❌ Error: NEO_USERNAME and NEO_PASSWORD environment variables must be set.")
        return

    db = GraphDB(uri, user, password)

    csv_file_path = "Data/Processed_People_Knowledge_Graph.csv"
    importer = KnowledgeGraphImporter(db, csv_file_path)
    
    importer.setup_constraints()
    importer.import_data()

    db.close()
    
    print("\n🎉 Knowledge graph import process complete!")

if __name__ == "__main__":
    main()

