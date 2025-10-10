#!/usr/bin/env python3
"""
Neo4j Knowledge Graph Import Script
Imports LinkedIn profile data from CSV into Neo4j following the optimized architecture.
"""

import os
from dotenv import load_dotenv
from src.graph_db import GraphDB
from src.importer import KnowledgeGraphImporter

# Load environment variables from .env file (override=True forces .env to take precedence)
load_dotenv(override=True)

def main():
    print("\n" + "=" * 80)
    print("🚀 Neo4j Knowledge Graph Importer")
    print("=" * 80 + "\n")
    
    # Get Neo4j credentials from environment (matching your .env file)
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO_USERNAME", "neo4j")  # Changed from NEO4J_USER
    NEO4J_PASSWORD = os.getenv("NEO_PASSWORD", "password")  # Changed from NEO4J_PASSWORD
    
    # Fix URI format for Neo4j Aura (remove port if using neo4j+s://)
    if "neo4j+s://" in NEO4J_URI or "neo4j+ssc://" in NEO4J_URI:
        # Remove :7687 port for Aura connections
        NEO4J_URI = NEO4J_URI.replace(":7687", "")
    
    # CSV file path
    CSV_PATH = "data/Final_Merged_Knowledge_Graph.csv"
    
    print(f"📡 Connecting to Neo4j at {NEO4J_URI}...")
    print(f"👤 User: {NEO4J_USER}")
    
    try:
        # Initialize database connection
        db = GraphDB(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # Initialize importer
        importer = KnowledgeGraphImporter(db, CSV_PATH)
        
        # Setup constraints and indexes
        importer.setup_constraints()
        
        # Import data
        importer.import_data()
        
        # Close connection
        db.close()
        
        print("\n✨ All done! Your knowledge graph is ready for queries.\n")
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}\n")
        raise

if __name__ == "__main__":
    main()
