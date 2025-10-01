# --- search.py ---
import os
import sys
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_db import GraphDB
from src.natural_language_search import NaturalLanguageSearch

def main():
    """
    The main function to run the interactive natural language search CLI.
    """
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO_USERNAME")
    password = os.getenv("NEO_PASSWORD")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([uri, user, password, openai_api_key]):
        print("❌ Error: NEO4J_URI, NEO_USERNAME, NEO_PASSWORD, and OPENAI_API_KEY environment variables must be set.")
        return

    db = GraphDB(uri, user, password)
    
    # Initialize our new search system
    search_engine = NaturalLanguageSearch(db, openai_api_key)
    
    print("\n--- Natural Language Knowledge Graph Search ---")
    print("Type your question, or type 'exit' to quit.")
    print("Examples: 'Who has machine learning skills?', 'Who worked at Google?'")
    print("-------------------------------------------------")

    while True:
        user_question = input("\nAsk a question > ").strip()

        if not user_question:
            continue
        if user_question.lower() == 'exit':
            break

        try:
            answer = search_engine.search(user_question)
            print(f"\nAnswer: {answer}")
        except Exception as e:
            print(f"An error occurred: {e}")

    db.close()
    print("Application exited.")


if __name__ == "__main__":
    main()
    

