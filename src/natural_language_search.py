# --- src/natural_language_search.py ---
import openai
import json
from src.query import QueryManager

class NaturalLanguageSearch:
    """
    Handles converting natural language questions into function calls and
    executing them against the Neo4j graph using OpenAI function calling.
    """
    def __init__(self, graph_db_driver, openai_api_key):
        """
        Initializes the search system.

        Args:
            graph_db_driver: An active instance of our GraphDB class.
            openai_api_key: Your OpenAI API key.
        """
        print("🔄 Initializing QueryManager...")
        self.query_manager = QueryManager(graph_db_driver)
        print("✅ QueryManager initialized successfully.")
        
        print("🔄 Initializing OpenAI client...")
        self.client = openai.OpenAI(api_key=openai_api_key)
        print("✅ OpenAI client initialized.")
        
        # Define available functions for OpenAI function calling
        self.functions = [
            {
                "name": "find_people_by_skill",
                "description": "Find people who have a specific skill (e.g., Python, machine learning, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill": {
                            "type": "string",
                            "description": "The skill to search for (will be converted to lowercase automatically)"
                        }
                    },
                    "required": ["skill"]
                }
            },
            {
                "name": "find_people_by_company",
                "description": "Find people who have worked at a specific company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "The name of the company to search for"
                        }
                    },
                    "required": ["company_name"]
                }
            },
            {
                "name": "find_person_by_name",
                "description": "Find a specific person by their name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the person to search for"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "find_colleagues_at_company",
                "description": "Find colleagues of a specific person at a given company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "person_id": {
                            "type": "integer",
                            "description": "The ID of the person to find colleagues for"
                        },
                        "company_name": {
                            "type": "string",
                            "description": "The name of the company where they worked together"
                        }
                    },
                    "required": ["person_id", "company_name"]
                }
            }
        ]
        print("✅ Function definitions loaded.")

    def search(self, question):
        """
        Takes a natural language question and returns the answer from the graph.
        """
        try:
            print(f"🔍 Processing question: {question}")
            
            # Step 1: Use OpenAI function calling to determine intent and extract parameters
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that can search a professional network knowledge graph. Use the provided functions to answer user questions about people, their skills, companies they worked for, and their colleagues."
                    },
                    {
                        "role": "user", 
                        "content": question
                    }
                ],
                functions=self.functions,
                function_call="auto"
            )

            message = response.choices[0].message
            
            # Step 2: Check if OpenAI wants to call a function
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                print(f"🔧 Calling function: {function_name} with args: {function_args}")
                
                # Step 3: Execute the appropriate function
                results = self._execute_function(function_name, function_args)
                
                # Step 4: Format and return results
                return self._format_results(question, function_name, function_args, results)
            
            else:
                # If no function was called, the question might not be answerable with available functions
                return "I'm sorry, I couldn't understand how to search for that information. I can help you find people by their skills, companies they worked at, or by their names. You can also ask me to find colleagues of specific people at companies."
                
        except Exception as e:
            print(f"❌ Error processing question: {e}")
            return f"An error occurred while processing your question: {str(e)}"

    def _execute_function(self, function_name, function_args):
        """
        Executes the specified function with the given arguments.
        """
        if function_name == "find_people_by_skill":
            return self.query_manager.find_people_by_skill(function_args["skill"])
        
        elif function_name == "find_people_by_company":
            return self.query_manager.find_people_by_company(function_args["company_name"])
        
        elif function_name == "find_person_by_name":
            return self.query_manager.find_person_by_name(function_args["name"])
        
        elif function_name == "find_colleagues_at_company":
            return self.query_manager.find_colleagues_at_company(
                function_args["person_id"], 
                function_args["company_name"]
            )
        
        else:
            raise ValueError(f"Unknown function: {function_name}")

    def _format_results(self, question, function_name, function_args, results):
        """
        Formats the query results into a natural language response.
        """
        if not results:
            return "No results found for your query."
        
        # Create a context-appropriate response based on the function called
        if function_name == "find_people_by_skill":
            skill = function_args["skill"]
            names = [result["name"] for result in results]
            if len(names) == 1:
                return f"I found 1 person with {skill} skills: {names[0]}."
            else:
                names_str = ", ".join(names[:-1]) + f", and {names[-1]}" if len(names) > 1 else names[0]
                return f"I found {len(names)} people with {skill} skills: {names_str}."
        
        elif function_name == "find_people_by_company":
            company = function_args["company_name"]
            names = [result["name"] for result in results]
            if len(names) == 1:
                return f"I found 1 person who worked at {company}: {names[0]}."
            else:
                names_str = ", ".join(names[:-1]) + f", and {names[-1]}" if len(names) > 1 else names[0]
                return f"I found {len(names)} people who worked at {company}: {names_str}."
        
        elif function_name == "find_person_by_name":
            name = function_args["name"]
            if len(results) == 1:
                person = results[0]
                return f"I found {person['name']}. Their headline is: {person['headline']}"
            else:
                names = [result["name"] for result in results]
                names_str = ", ".join(names)
                return f"I found {len(results)} people matching '{name}': {names_str}."
        
        elif function_name == "find_colleagues_at_company":
            person_id = function_args["person_id"]
            company = function_args["company_name"]
            colleagues = [result["colleague_name"] for result in results]
            if len(colleagues) == 1:
                return f"I found 1 colleague of person ID {person_id} at {company}: {colleagues[0]}."
            else:
                colleagues_str = ", ".join(colleagues[:-1]) + f", and {colleagues[-1]}" if len(colleagues) > 1 else colleagues[0]
                return f"I found {len(colleagues)} colleagues of person ID {person_id} at {company}: {colleagues_str}."
        
        # Fallback formatting
        return f"I found {len(results)} results for your query."
