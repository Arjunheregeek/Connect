"""
The `src` package contains the core modules for the Professional Network Knowledge Graph project.

Modules:
- graph_db: Handles interactions with the Neo4j database.
- importer: Manages data import into the knowledge graph.
- query: Contains predefined queries for the knowledge graph.
"""

# This file makes the src directory a Python package.

from .graph_db import GraphDB
from .importer import KnowledgeGraphImporter
from .query import QueryManager