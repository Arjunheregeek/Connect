# --- src/natural_language_search.py ---
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
import os

# Predefined schema to avoid slow schema fetching
GRAPH_SCHEMA = """
Node properties are the following:
Person {id: INTEGER, name: STRING, linkedin_profile: STRING, email: STRING, phone: STRING, location: STRING, headline: STRING, summary: STRING, followers_count: FLOAT, total_experience_months: FLOAT},
Company {url: STRING, name: STRING},
Institution {url: STRING, name: STRING},
Skill {name: STRING}

Relationship properties are the following:
WORKS_AT {title: STRING, start_date: STRING, end_date: STRING, duration_months: FLOAT, description: STRING, location: STRING},
STUDIED_AT {degree: STRING, start_year: INTEGER, end_year: INTEGER}

The relationships are the following:
(:Person)-[:WORKS_AT]->(:Company),
(:Person)-[:STUDIED_AT]->(:Institution),
(:Person)-[:HAS_SKILL]->(:Skill)
"""

class NaturalLanguageSearch:
    """
    Handles converting natural language questions into Cypher queries and
    executing them against the Neo4j graph using LangChain.
    """
    def __init__(self, graph_db_driver, openai_api_key):
        """
        Initializes the search system.

        Args:
            graph_db_driver: An active instance of our GraphDB class.
            openai_api_key: Your OpenAI API key.
        """
        print("🔄 Initializing Neo4jGraph connection...")
        # This Neo4jGraph object from LangChain is a wrapper around our database.
        # It's used by LangChain to automatically learn the graph's schema.
        try:
            self.graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI"),
                username=os.getenv("NEO_USERNAME"),
                password=os.getenv("NEO_PASSWORD"),
                refresh_schema=False  # Skip automatic schema refresh to speed up initialization
            )
            print("✅ Neo4jGraph initialized successfully.")
            
            # Set the predefined schema instead of fetching it
            print("🔄 Loading predefined schema...")
            self.graph.schema = GRAPH_SCHEMA
            print("✅ Schema loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to initialize Neo4jGraph: {e}")
            raise

        print("🔄 Initializing OpenAI LLM...")
        # Instantiate the OpenAI LLM, which will be used to generate Cypher
        llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=openai_api_key)
        print("✅ OpenAI LLM initialized.")

        print("🔄 Building GraphCypherQAChain...")
        # This is the core LangChain "chain" that performs the magic.
        # It takes the graph schema and an LLM and knows how to convert
        # a question into a Cypher query.
        self.chain = GraphCypherQAChain.from_llm(
            graph=self.graph,
            llm=llm,
            verbose=True,  # Set to True to see the generated Cypher in your terminal
            allow_dangerous_requests=True  # Required acknowledgment for using AI-generated queries
        )
        print("✅ GraphCypherQAChain ready!")

    def search(self, question):
        """
        Takes a natural language question and returns the answer from the graph.
        """
        result = self.chain.invoke({"query": question})
        return result['result']
