from neo4j import GraphDatabase, exceptions
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GraphDB:
    """
    Enhanced GraphDB with connection pooling and performance optimizations.
    Maintains backward compatibility while adding async support.
    """
    def __init__(self, uri, user, password):
        """
        Initializes the connection to the Neo4j database.
        """
        self.driver = None
        self.uri = uri
        self.user = user 
        self.password = password
        
        try:
            # Enhanced driver configuration for performance
            self.driver = GraphDatabase.driver(
                uri, 
                auth=(user, password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=30,
                keep_alive=True,
                max_transaction_retry_time=15
            )
            self.driver.verify_connectivity()
            logger.info("✅ Connection to Neo4j database established successfully.")
            print("✅ Connection to Neo4j database established successfully.")
        except (exceptions.AuthError, exceptions.ServiceUnavailable) as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            print(f"❌ Failed to connect to Neo4j: {e}")
            exit()

    def close(self):
        """Closes the database connection driver to release resources."""
        if self.driver is not None:
            self.driver.close()
            logger.info("Neo4j connection closed.")
            print("Neo4j connection closed.")

    def execute_query(self, query, params=None):
        """
        Executes a Cypher query within a managed transaction (synchronous).
        Maintains backward compatibility.
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self._execute_transaction, query, params)
            return result
    
    def execute_read_query(self, query, params=None):
        """
        Executes a read-only Cypher query for better performance.
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(self._execute_transaction, query, params)
            return result

    @staticmethod
    def _execute_transaction(tx, query, params=None):
        """
        Static method that executes the actual transaction.
        """
        result = tx.run(query, params or {})
        return [record.data() for record in result]
    
    async def execute_query_async(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Async version of execute_query for use with connection pool.
        """
        # Import here to avoid circular imports
        from mcp.utils.connection_pool import connection_pool
        
        try:
            # Initialize connection pool if not already done
            if not connection_pool._initialized:
                await connection_pool.initialize()
            
            # Execute query through connection pool
            return await connection_pool.execute_read_query(query, params)
            
        except Exception as e:
            logger.error(f"Async query execution failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            raise
    
    async def health_check_async(self) -> Dict[str, Any]:
        """Async health check using connection pool"""
        try:
            from mcp.utils.connection_pool import connection_pool
            return await connection_pool.health_check()
        except Exception as e:
            logger.error(f"Async health check failed: {str(e)}")
            return {
                "database_connected": False,
                "error": str(e),
                "connection_pool_healthy": False
            }

