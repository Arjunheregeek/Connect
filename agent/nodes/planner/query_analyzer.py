"""
Query Analyzer Module

Analyzes user queries to extract intent, entities, and requirements.
This module focuses solely on understanding what the user is asking for.
"""

import re
from typing import Dict, Any, List, Tuple


class QueryAnalyzer:
    """
    Analyzes user queries to extract intent, entities, and requirements.
    
    This class uses pattern matching and keyword analysis to understand
    what the user is looking for and what kind of search strategy to use.
    """
    
    # Define query intent patterns
    INTENT_PATTERNS = {
        'find_person': [
            r'find.*person.*named?.*(\w+)',
            r'who is (\w+)',
            r'tell me about (\w+)',
            r'(\w+\s+\w+).*profile'
        ],
        'find_by_skill': [
            r'find.*people.*with.*skill[s]?.*(\w+)',
            r'who.*knows?.*(\w+)',
            r'experts?.*in.*(\w+)',
            r'developers?.*(\w+)',
            r'specialists?.*(\w+)'
        ],
        'find_by_company': [
            r'find.*people.*at.*(\w+)',
            r'who.*works?.*at.*(\w+)',
            r'employees?.*at.*(\w+)',
            r'(\w+).*team.*members?'
        ],
        'find_colleagues': [
            r'(\w+).*colleagues?',
            r'who.*works?.*with.*(\w+)',
            r'(\w+).*team.*mates?'
        ],
        'natural_language': [
            r'.*\?$',  # Questions ending with ?
            r'tell me.*',
            r'show me.*',
            r'i.*want.*to.*know'
        ]
    }
    
    @classmethod
    def analyze_query(cls, query: str) -> Dict[str, Any]:
        """
        Analyze user query to extract intent and entities.
        
        Args:
            query: User's input query string
            
        Returns:
            Dictionary containing:
            - intent: Primary intent category
            - entities: Extracted entities (names, skills, companies)
            - confidence: Analysis confidence (0.0-1.0)
            - keywords: Important keywords from query
        """
        query_lower = query.lower().strip()
        
        # Extract intent
        intent, entities, confidence = cls._extract_intent_and_entities(query_lower)
        
        # Extract keywords
        keywords = cls._extract_keywords(query_lower)
        
        return {
            'intent': intent,
            'entities': entities,
            'confidence': confidence,
            'keywords': keywords,
            'original_query': query
        }
    
    @classmethod
    def _extract_intent_and_entities(cls, query: str) -> Tuple[str, Dict[str, Any], float]:
        """Extract primary intent and associated entities from query."""
        
        # Check each intent pattern
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    entities = {}
                    confidence = 0.8
                    
                    # Extract entities based on intent
                    if intent == 'find_person':
                        entities['person_name'] = match.group(1)
                    elif intent == 'find_by_skill':
                        entities['skill'] = match.group(1)
                        confidence = 0.9  # High confidence for skill searches
                    elif intent == 'find_by_company':
                        entities['company'] = match.group(1)
                    elif intent == 'find_colleagues':
                        entities['person_name'] = match.group(1)
                    
                    return intent, entities, confidence
        
        # Default to natural language search
        return 'natural_language', {}, 0.6
    
    @classmethod
    def _extract_keywords(cls, query: str) -> List[str]:
        """Extract important keywords from the query."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
            'may', 'might', 'must', 'can', 'find', 'who', 'what', 'where', 'when', 
            'why', 'how'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords