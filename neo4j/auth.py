from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO_USERNAME"), os.getenv("NEO_PASSWORD"))

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("✅ Successfully connected to the Neo4j database.")
except Exception as e:
    print(f"❌ Failed to connect to the Neo4j database: {e}")