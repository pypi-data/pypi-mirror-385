from enum import Enum
from typing import List, Dict, Any, LiteralString, Optional

from blarify.repositories.graph_db_manager.dtos.node_search_result_dto import ReferenceSearchResultDTO


class ENVIRONMENT(Enum):
    MAIN = "main"
    DEV = "dev"


class AbstractDbManager:
    def close(self):
        """Close the connection to the database."""
        raise NotImplementedError

    def save_graph(self, nodes, edges):
        """Save nodes and edges to the database."""
        raise NotImplementedError

    def create_nodes(self, nodeList):
        """Create nodes in the database."""
        raise NotImplementedError

    def create_edges(self, edgesList):
        """Create edges between nodes in the database."""
        raise NotImplementedError

    def detatch_delete_nodes_with_path(self, path):
        """Detach and delete nodes matching the given path."""
        raise NotImplementedError

    def query(
        self, cypher_query: LiteralString, parameters: Optional[Dict[str, Any]] = None, transaction: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.

        Args:
            cypher_query: The Cypher query string to execute
            parameters: Optional dictionary of parameters for the query

        Returns:
            List of dictionaries containing the query results
        """
        raise NotImplementedError

    def get_node_by_id(
        self,
        node_id: str,
    ) -> ReferenceSearchResultDTO:
        """
        Retrieve a node from the database by its ID.

        Args:
            node_id: The ID of the node to retrieve.

        Returns:
            A dictionary representing the node, or None if not found.
        """
        raise NotImplementedError

    def get_node_by_name_and_type(
        self,
        name: str,
        node_type: str,
    ):
        """
        Retrieve nodes by name and type from the database.

        Args:
            name: Name of the node to search for
            node_type: Type/label of the node to search for

        Returns:
            List of node data transfer objects

        Note:
            entity_id (mandatory) and repo_id (optional) are injected from manager instance.
            If repo_id is None, searches across all repos for the entity.
        """
        raise NotImplementedError
