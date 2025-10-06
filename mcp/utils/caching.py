# --- mcp/utils/caching.py ---
import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with value and metadata"""
    value: Any
    timestamp: float
    hits: int = 0
    ttl: float = 300.0  # 5 minutes default

class LRUCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired": 0
        }
    
    def _generate_key(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generate cache key from tool name and arguments"""
        # Create deterministic hash of arguments
        args_str = json.dumps(arguments, sort_keys=True)
        key_data = f"{tool_name}:{args_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Get cached result if available and not expired"""
        key = self._generate_key(tool_name, arguments)
        
        async with self._lock:
            if key not in self.cache:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss for {tool_name}")
                return None
            
            entry = self.cache[key]
            current_time = time.time()
            
            # Check if expired
            if current_time - entry.timestamp > entry.ttl:
                del self.cache[key]
                self._stats["expired"] += 1
                self._stats["misses"] += 1
                logger.debug(f"Cache expired for {tool_name}")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.hits += 1
            self._stats["hits"] += 1
            
            logger.debug(f"Cache hit for {tool_name} (hits: {entry.hits})")
            return entry.value
    
    async def set(self, tool_name: str, arguments: Dict[str, Any], value: Any, ttl: Optional[float] = None) -> None:
        """Cache a result"""
        key = self._generate_key(tool_name, arguments)
        cache_ttl = ttl or self.default_ttl
        
        async with self._lock:
            # Remove oldest entries if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self._stats["evictions"] += 1
                logger.debug(f"Evicted cache entry: {oldest_key}")
            
            self.cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=cache_ttl
            )
            
            logger.debug(f"Cached result for {tool_name} (TTL: {cache_ttl}s)")
    
    async def invalidate(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Invalidate specific cache entry"""
        key = self._generate_key(tool_name, arguments)
        
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Invalidated cache for {tool_name}")
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                "total_hits": self._stats["hits"],
                "total_misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "expired": self._stats["expired"],
                "entries": [
                    {
                        "key": key[:16] + "...",
                        "hits": entry.hits,
                        "age": time.time() - entry.timestamp,
                        "ttl": entry.ttl
                    }
                    for key, entry in list(self.cache.items())[:10]  # Show top 10
                ]
            }

class CacheManager:
    """Global cache manager for MCP server"""
    
    def __init__(self):
        # Different cache configurations for different tool types
        self.caches = {
            # Fast-changing data (short TTL)
            "dynamic": LRUCache(max_size=500, default_ttl=60.0),  # 1 minute
            
            # Semi-static data (medium TTL) 
            "standard": LRUCache(max_size=1000, default_ttl=300.0),  # 5 minutes
            
            # Stable data (long TTL)
            "stable": LRUCache(max_size=2000, default_ttl=1800.0),  # 30 minutes
        }
        
        # Define cache strategies for each tool
        self.tool_strategies = {
            # Dynamic data - people's current status might change
            "find_person_by_name": "dynamic",
            "get_person_details": "dynamic",
            "get_person_job_descriptions": "dynamic",
            "natural_language_search": "dynamic",
            
            # Standard caching - skills and company data
            "find_people_by_skill": "standard",
            "find_people_by_company": "standard",
            "get_person_skills": "standard",
            "find_colleagues_at_company": "standard",
            "get_person_colleagues": "standard",
            "find_people_by_experience_level": "standard",
            "get_company_employees": "standard",
            "search_job_descriptions_by_keywords": "standard",
            "find_technical_skills_in_descriptions": "standard",
            "analyze_career_progression": "standard",
            
            # Stable data - institutional and location data changes rarely
            "find_people_by_institution": "stable",
            "find_people_by_location": "stable",
            "find_people_with_multiple_skills": "stable",
            "get_skill_popularity": "stable",
            "find_leadership_indicators": "stable",
            "find_achievement_patterns": "stable",
            "find_domain_experts": "stable",
            "find_similar_career_paths": "stable",
            "find_role_transition_patterns": "stable",
            
            # No caching for system tools
            "health_check": None
        }
    
    def _get_cache_for_tool(self, tool_name: str) -> Optional[LRUCache]:
        """Get appropriate cache instance for tool"""
        strategy = self.tool_strategies.get(tool_name)
        if strategy is None:
            return None
        return self.caches.get(strategy)
    
    async def get_cached_result(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Get cached result for tool call"""
        cache = self._get_cache_for_tool(tool_name)
        if cache is None:
            return None
        
        return await cache.get(tool_name, arguments)
    
    async def cache_result(self, tool_name: str, arguments: Dict[str, Any], result: Any) -> None:
        """Cache result for tool call"""
        cache = self._get_cache_for_tool(tool_name)
        if cache is None:
            return
        
        await cache.set(tool_name, arguments, result)
    
    async def invalidate_tool_cache(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Invalidate cache for specific tool call"""
        cache = self._get_cache_for_tool(tool_name)
        if cache is None:
            return False
        
        return await cache.invalidate(tool_name, arguments)
    
    async def clear_all_caches(self) -> None:
        """Clear all caches"""
        for cache in self.caches.values():
            await cache.clear()
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        stats = {}
        for cache_type, cache in self.caches.items():
            stats[cache_type] = await cache.get_stats()
        
        return {
            "cache_stats": stats,
            "tool_strategies": self.tool_strategies
        }

# Global cache manager instance
cache_manager = CacheManager()