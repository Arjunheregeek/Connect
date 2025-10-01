from neo4j import GraphDatabase, exceptions
import os

class GraphDB:
    """
    Manages all interactions with the Neo4j database, including connection,
    query execution, and closing the connection.
    """
    def __init__(self, uri, user, password):
        """
        Initializes the connection to the Neo4j database.
        
        Args:
            uri (str): The connection URI for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("✅ Connection to Neo4j database established successfully.")
        except (exceptions.AuthError, exceptions.ServiceUnavailable) as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            exit()

    def close(self):
        """
        Closes the database connection driver to release resources.
        """
        if self.driver is not None:
            self.driver.close()
            print("Neo4j connection closed.")

    def execute_query(self, query, params=None):
        """
        Executes a Cypher query within a managed transaction.
        
        Args:
            query (str): The Cypher query to be executed.
            params (dict, optional): A dictionary of parameters to pass to the query.
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._execute_transaction, query, params)
            return result

    @staticmethod
    def _execute_transaction(tx, query, params=None):
        """
        A static method that executes the actual transaction. Called by session's
        execute_write or execute_read methods.
        """
        result = tx.run(query, params or {})
        return [record for record in result]

