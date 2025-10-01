# --- run.py ---
import os
import sys
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_db import GraphDB
from src.query import QueryManager

def print_help():
    """Prints a help message with available commands."""
    print("\n--- Professional Network Knowledge Graph CLI ---")
    print("Available Commands:")
    print("  find_skill <skill_name>        - Find people with a specific skill.")
    print("  find_company <company_name>      - Find people who worked at a company.")
    print("  find_person <full_name>        - Find a person by their name.")
    print("  find_colleagues <id> <company> - Find who a person worked with at a company.")
    print("  help                           - Show this help message.")
    print("  exit                           - Exit the application.")
    print("-------------------------------------------------")

def main():
    """
    The main function to run the interactive command-line interface.
    """
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO_USERNAME")
    password = os.getenv("NEO_PASSWORD")

    if not all([uri, user, password]):
        print("❌ Error: NEO4J_URI, NEO_USERNAME, and NEO_PASSWORD environment variables must be set.")
        return

    db = GraphDB(uri, user, password)
    queries = QueryManager(db)
    
    print_help()

    while True:
        user_input = input("\nEnter command > ").strip()
        if not user_input:
            continue

        parts = user_input.split()
        command = parts[0].lower()
        
        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "find_skill" and len(parts) > 1:
            args = " ".join(parts[1:])
            results = queries.find_people_by_skill(args)
            print(f"Found {len(results)} people with the skill '{args}':")
            for r in results:
                print(f"  - {r['name']} ({r['headline']})")
        elif command == "find_company" and len(parts) > 1:
            args = " ".join(parts[1:])
            results = queries.find_people_by_company(args)
            print(f"Found {len(results)} people who worked at '{args}':")
            for r in results:
                print(f"  - {r['name']} ({r['headline']})")
        elif command == "find_person" and len(parts) > 1:
            args = " ".join(parts[1:])
            results = queries.find_person_by_name(args)
            print(f"Found {len(results)} people with the name '{args}':")
            for r in results:
                print(f"  - {r['name']} ({r['profile']})")
        elif command == "find_colleagues" and len(parts) >= 3:
            try:
                person_id = int(parts[1])
                company_name = " ".join(parts[2:])
                results = queries.find_colleagues_at_company(person_id, company_name)
                print(f"Found {len(results)} colleagues of Person ID {person_id} at '{company_name}':")
                for r in results:
                    print(f"  - {r['colleague_name']} ({r['colleague_headline']})")
            except ValueError:
                print("❌ Invalid command: The 'id' for find_colleagues must be a number.")
        else:
            print("❌ Invalid command or missing arguments. Type 'help' for options.")

    db.close()
    print("Application exited.")


if __name__ == "__main__":
    main()

