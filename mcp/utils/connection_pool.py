# --- mcp/utils/connection_pool.py ---
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import time
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from mcp.config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class ConnectionStats:
    """Connection pool statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_queries: int = 0
    avg_query_time: float = 0.0
    last_error: Optional[str] = None

class Neo4jConnectionPool:
    """Enhanced Neo4j connection pool with monitoring and optimization"""
    
    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
        self.stats = ConnectionStats()
        self._query_times: List[float] = []
        self._max_query_history = 1000
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the connection pool"""
        if self._initialized:
            return
        
        try:
            # Enhanced driver configuration for performance
            self.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
                # Connection pool settings
                max_connection_lifetime=3600,  # 1 hour
                max_connection_pool_size=50,   # Max connections
                connection_acquisition_timeout=30,  # 30 seconds timeout
                # Performance settings
                keep_alive=True,
                max_transaction_retry_time=15,
                # Logging
                encrypted=True,
                trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
            )
            
            # Verify connectivity
            await self.verify_connectivity()
            self._initialized = True
            
            logger.info(f"Neo4j connection pool initialized with max_pool_size=50")
            
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection pool: {str(e)}")
            self.stats.last_error = str(e)
            raise
    
    async def verify_connectivity(self) -> bool:
        """Verify database connectivity"""
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                if record and record["test"] == 1:
                    logger.info("Neo4j connectivity verified")
                    return True
                return False
        except Exception as e:
            logger.error(f"Neo4j connectivity check failed: {str(e)}")
            self.stats.failed_connections += 1
            self.stats.last_error = str(e)
            return False
    
    @asynccontextmanager
    async def get_session(
        self, 
        database: Optional[str] = None,
        access_mode: str = "READ"
    ):
        """Get a database session with connection pooling and monitoring"""
        if not self._initialized:
            await self.initialize()
        
        session = None
        start_time = time.time()
        
        try:
            # Get session from pool
            session = self.driver.session(
                database=database,
                default_access_mode=access_mode
            )
            
            async with self._lock:
                self.stats.active_connections += 1
                self.stats.total_connections += 1
            
            logger.debug(f"Acquired database session (mode: {access_mode})")
            yield session
            
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            async with self._lock:
                self.stats.failed_connections += 1
                self.stats.last_error = str(e)
            raise
            
        finally:
            # Clean up and update stats
            if session:
                await session.close()
                
                query_time = time.time() - start_time
                async with self._lock:
                    self.stats.active_connections -= 1
                    self.stats.total_queries += 1
                    
                    # Track query times for performance monitoring
                    self._query_times.append(query_time)
                    if len(self._query_times) > self._max_query_history:
                        self._query_times.pop(0)
                    
                    # Calculate average query time
                    if self._query_times:
                        self.stats.avg_query_time = sum(self._query_times) / len(self._query_times)
                
                logger.debug(f"Released database session (query_time: {query_time:.3f}s)")
    
    async def execute_read_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a read query with connection pooling"""
        async with self.get_session(access_mode="READ") as session:
            try:
                result = await session.run(query, parameters or {})
                records = await result.data()
                logger.debug(f"Read query executed: {len(records)} records returned")
                return records
            except Exception as e:
                logger.error(f"Read query failed: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                raise
    
    async def execute_write_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a write query with connection pooling"""
        async with self.get_session(access_mode="WRITE") as session:
            try:
                result = await session.run(query, parameters or {})
                records = await result.data()
                logger.debug(f"Write query executed: {len(records)} records affected")
                return records
            except Exception as e:
                logger.error(f"Write query failed: {str(e)}")
                logger.error(f"Query: {query}")
                logger.error(f"Parameters: {parameters}")
                raise
    
    async def execute_transaction(self, transaction_func, *args, **kwargs):
        """Execute a transaction with retry logic"""
        async with self.get_session() as session:
            try:
                result = await session.execute_write(transaction_func, *args, **kwargs)
                logger.debug("Transaction executed successfully")
                return result
            except Exception as e:
                logger.error(f"Transaction failed: {str(e)}")
                raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        async with self._lock:
            # Get driver pool info if available
            pool_info = {}
            if self.driver and hasattr(self.driver, '_pool'):
                try:
                    pool_info = {
                        "pool_size": getattr(self.driver._pool, 'size', 'unknown'),
                        "in_use": getattr(self.driver._pool, 'in_use', 'unknown'),
                    }
                except:
                    pool_info = {"pool_info": "unavailable"}
            
            return {
                "connection_stats": {
                    "total_connections": self.stats.total_connections,
                    "active_connections": self.stats.active_connections,
                    "failed_connections": self.stats.failed_connections,
                    "total_queries": self.stats.total_queries,
                    "avg_query_time_ms": round(self.stats.avg_query_time * 1000, 2),
                    "last_error": self.stats.last_error
                },
                "pool_info": pool_info,
                "query_performance": {
                    "recent_queries": len(self._query_times),
                    "slowest_query_ms": round(max(self._query_times) * 1000, 2) if self._query_times else 0,
                    "fastest_query_ms": round(min(self._query_times) * 1000, 2) if self._query_times else 0,
                }
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Test basic connectivity
            connectivity_ok = await self.verify_connectivity()
            
            # Test query performance
            start_time = time.time()
            async with self.get_session() as session:
                result = await session.run("MATCH (n) RETURN count(n) as node_count LIMIT 1")
                record = await result.single()
                node_count = record["node_count"] if record else 0
            query_time = time.time() - start_time
            
            # Get current stats
            stats = await self.get_stats()
            
            return {
                "database_connected": connectivity_ok,
                "node_count": node_count,
                "query_response_time_ms": round(query_time * 1000, 2),
                "connection_pool_healthy": self.stats.failed_connections < 10,  # Threshold
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "database_connected": False,
                "error": str(e),
                "connection_pool_healthy": False
            }
    
    async def close(self) -> None:
        """Close the connection pool"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection pool closed")

# Global connection pool instance
connection_pool = Neo4jConnectionPool()