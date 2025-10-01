# --- src/natural_language_search.py ---
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

# Predefined schema to avoid slow schema fetching
GRAPH_SCHEMA = """
Node properties are the following:
Person {id: INTEGER, name: STRING, linkedin_profile: STRING, email: STRING, phone: STRING, location: STRING, headline: STRING, summary: STRING, followers_count: FLOAT, total_experience_months: FLOAT},
Company {url: STRING, name: STRING},
Institution {url: STRING, name: STRING},
Skill {name: STRING} -- NOTE: Skill names are stored in lowercase

Relationship properties are the following:
WORKS_AT {title: STRING, start_date: STRING, end_date: STRING, duration_months: FLOAT, description: STRING, location: STRING},
STUDIED_AT {degree: STRING, start_year: INTEGER, end_year: INTEGER}

The relationships are the following:
(:Person)-[:WORKS_AT]->(:Company),
(:Person)-[:STUDIED_AT]->(:Institution),
(:Person)-[:HAS_SKILL]->(:Skill)

IMPORTANT: When searching for skills, always use lowercase for skill names.
Examples:
- For "Machine Learning" skills: MATCH (p:Person)-[:HAS_SKILL]->(s:Skill {name: 'machine learning'})
- For "Python" skills: MATCH (p:Person)-[:HAS_SKILL]->(s:Skill {name: 'python'})
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
        
        # Custom prompt to emphasize lowercase skills
        cypher_prompt_template = PromptTemplate(
            input_variables=["schema", "question"],
            template="""Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

CRITICAL: When searching for skills, ALWAYS use lowercase for skill names.
For example:
- "Machine Learning" becomes 'machine learning'
- "Python" becomes 'python'
- "Data Science" becomes 'data science'

Schema:
{schema}

The question is:
{question}

Cypher query:"""
        )

        # Custom prompt for generating the final answer
        qa_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an assistant that helps answer questions about a professional network knowledge graph.

Based on the following context from the database query results, provide a helpful and direct answer to the user's question.

Context: {context}

Question: {question}

If the context contains names or data, list them clearly. If the context is empty, explain that no results were found.

Answer:"""
        )

        self.chain = GraphCypherQAChain.from_llm(
            graph=self.graph,
            llm=llm,
            verbose=True,  # Set to True to see the generated Cypher in your terminal
            allow_dangerous_requests=True,  # Required acknowledgment for using AI-generated queries
            cypher_prompt=cypher_prompt_template
        )
        print("✅ GraphCypherQAChain ready!")

    def search(self, question):
        """
        Takes a natural language question and returns the answer from the graph.
        """
        # Step 1: Get the raw result from the chain
        result = self.chain.invoke({"query": question})
        
        # Step 2: If we have context data, use a separate LLM call to format the answer
        if result.get('context') and len(result['context']) > 0:
            # Create a separate LLM instance for answer formatting
            answer_llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
            
            # Format the context data into a readable string
            context_data = result['context']
            context_str = "\n".join([f"- {list(item.values())[0]}" for item in context_data])
            
            # Create a prompt for the answer generation
            answer_prompt = f"""Based on the following database query results, provide a clear and helpful answer to the user's question.

Question: {question}

Database Results:
{context_str}

Please provide a natural, conversational answer that lists the people found."""
            
            # Get the formatted answer
            formatted_answer = answer_llm.invoke(answer_prompt)
            return formatted_answer.content
        else:
            # If no context, return the original result
            return result['result']
