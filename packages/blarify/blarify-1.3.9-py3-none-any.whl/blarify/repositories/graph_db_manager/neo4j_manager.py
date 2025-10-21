import os
import time
from typing import Any, List, Dict, LiteralString, Optional

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase, ManagedTransaction, exceptions
import logging

from blarify.repositories.graph_db_manager.adapters.node_search_result_adapter import Neo4jNodeSearchResultAdapter
from blarify.repositories.graph_db_manager.db_manager import AbstractDbManager, ENVIRONMENT
from blarify.repositories.graph_db_manager.dtos.node_search_result_dto import ReferenceSearchResultDTO
from blarify.repositories.graph_db_manager.dtos.node_found_by_name_type import NodeFoundByNameTypeDto
from blarify.repositories.graph_db_manager.queries import get_node_by_id_query, get_node_by_name_and_type_query

logger = logging.getLogger(__name__)

# Disable Neo4j warning logs
neo4j_logger = logging.getLogger("neo4j")
neo4j_logger.setLevel(logging.ERROR)

load_dotenv()


class Neo4jManager(AbstractDbManager):
    entity_id: str
    repo_ids: Optional[list[str]]  # List of repo IDs or None for entity-wide queries
    driver: Driver

    def __init__(
        self,
        repo_id: Optional[str | list[str]] = None,
        entity_id: Optional[str] = None,
        environment: Optional[ENVIRONMENT] = None,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_connections: int = 50,
    ):
        uri = uri or os.getenv("NEO4J_URI")
        user = user or os.getenv("NEO4J_USERNAME")
        password = password or os.getenv("NEO4J_PASSWORD")

        if not uri or not user or not password:
            raise ValueError("Missing required Neo4j connection parameters")

        retries = 3
        for attempt in range(retries):
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_pool_size=max_connections)
                break
            except exceptions.ServiceUnavailable as e:
                if attempt < retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    raise e

        # Convert single repo_id to list for consistent handling
        if isinstance(repo_id, str):
            self.repo_ids = [repo_id]
        elif isinstance(repo_id, list):
            self.repo_ids = repo_id
        else:
            self.repo_ids = None

        self.entity_id = entity_id or "default_user"
        self.environment = environment or ENVIRONMENT.MAIN

    @property
    def repo_id(self) -> Optional[str]:
        """Backward compatibility property - returns first repo_id or None."""
        return self.repo_ids[0] if self.repo_ids and len(self.repo_ids) > 0 else None

    def close(self):
        # Close the connection to the database
        self.driver.close()

    def save_graph(self, nodes: List[Any], edges: List[Any]):
        self.create_nodes(nodes)
        self.create_edges(edges)

    def create_nodes(self, nodeList: List[Any]):
        # Function to create nodes in the Neo4j database
        if self.repo_id is None:
            raise ValueError("repo_id is required for creating nodes. Cannot create nodes with entity-wide scope.")

        with self.driver.session() as session:
            session.execute_write(
                self._create_nodes_txn,
                nodeList,
                1000,
                repoId=self.repo_id,
                entityId=self.entity_id,
                environment=self.environment.value,
            )

    def create_edges(self, edgesList: List[Any]):
        # Function to create edges between nodes in the Neo4j database
        if self.repo_id is None:
            raise ValueError("repo_id is required for creating edges. Cannot create edges with entity-wide scope.")

        with self.driver.session() as session:
            session.execute_write(
                self._create_edges_txn,
                edgesList,
                1000,
                entityId=self.entity_id,
                repoId=self.repo_id,
                environment=self.environment.value,
            )

    @staticmethod
    def _create_nodes_txn(
        tx: ManagedTransaction, nodeList: List[Any], batch_size: int, repoId: str, entityId: str, environment: str
    ):
        node_creation_query = """
        CALL apoc.periodic.iterate(
            "UNWIND $nodeList AS node RETURN node",
            "CALL apoc.merge.node(
            node.extra_labels + [node.type, 'NODE'],
            {hashed_id: node.attributes.hashed_id, repoId: $repoId, entityId: $entityId, environment: $environment, diff_identifier: node.attributes.diff_identifier},
            node.attributes,
            node.attributes
            )
            YIELD node as n RETURN count(n) as count",
            {batchSize: $batchSize, parallel: false, iterateList: true, params: {nodeList: $nodeList, repoId: $repoId, entityId: $entityId, environment: $environment}}
        )
        YIELD batches, total, errorMessages, updateStatistics
        RETURN batches, total, errorMessages, updateStatistics
        """

        result = tx.run(
            node_creation_query,
            nodeList=nodeList,
            batchSize=batch_size,
            repoId=repoId,
            entityId=entityId,
            environment=environment,
        )

        # Fetch the result
        for record in result:
            logger.info(f"Created {record['total']} nodes")
            if record["errorMessages"]:
                logger.error(f"Error creating nodes: {record['errorMessages']}")
            print(record)

    @staticmethod
    def _create_edges_txn(
        tx: ManagedTransaction, edgesList: List[Any], batch_size: int, entityId: str, repoId: str, environment: str
    ):
        # Cypher query using apoc.periodic.iterate for creating edges
        edge_creation_query = """
        CALL apoc.periodic.iterate(
            "UNWIND $edgesList AS edgeObject RETURN edgeObject",
            "MATCH (node1:NODE {node_id: edgeObject.sourceId, repoId: $repoId, entityId: $entityId, environment: $environment}) 
            MATCH (node2:NODE {node_id: edgeObject.targetId, repoId: $repoId, entityId: $entityId, environment: $environment}) 
            CALL apoc.merge.relationship(
            node1, 
            edgeObject.type, 
            apoc.map.removeKeys(edgeObject, ['sourceId', 'targetId', 'type']), 
            apoc.map.removeKeys(edgeObject, ['sourceId', 'targetId', 'type']), 
            node2, 
            apoc.map.removeKeys(edgeObject, ['sourceId', 'targetId', 'type'])
            ) 
            YIELD rel RETURN count(rel) as count",
            {batchSize: $batchSize, parallel: false, iterateList: true, params: {edgesList: $edgesList, entityId: $entityId, repoId: $repoId, environment: $environment}}
        )
        YIELD batches, total, errorMessages, updateStatistics
        RETURN batches, total, errorMessages, updateStatistics
        """
        # Execute the query
        result = tx.run(
            edge_creation_query,
            edgesList=edgesList,
            batchSize=batch_size,
            entityId=entityId,
            repoId=repoId,
            environment=environment,
        )

        # Fetch the result
        for record in result:
            logger.info(f"Created {record['total']} edges")
            print(record)

    @staticmethod
    def run_transaction(tx: ManagedTransaction, query: LiteralString, params: Dict[str, Any] = {}, entity: str = ""):
        result = tx.run(query, params)
        records = list(result)  # Convert to list to return the records

        for record in records:
            print("Created record: ", record)
            print(f"Created {record['total']} {entity}")

        return records  # Return the records so execute_write can access them

    def detatch_delete_nodes_with_path(self, path: str):
        if self.repo_id is None:
            raise ValueError("repo_id is required for deleting nodes. Cannot delete nodes with entity-wide scope.")

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n {path: $path, repoId: $repo_id, entityId: $entity_id})
                DETACH DELETE n
                """,
                path=path,
                repo_id=self.repo_id,
                entity_id=self.entity_id,
            )
            return result.data()

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
        if parameters is None:
            parameters = {}

        # Inject repo_ids as list (or None for entity-wide queries)
        if "repo_ids" not in parameters:
            parameters["repo_ids"] = self.repo_ids
        # Also inject repo_id for backward compatibility (first repo or None)
        if "repo_id" not in parameters:
            parameters["repo_id"] = self.repo_id
        if "entity_id" not in parameters:
            parameters["entity_id"] = self.entity_id

        try:
            with self.driver.session() as session:
                result = []
                if transaction:
                    result = session.execute_write(
                        Neo4jManager.run_transaction, cypher_query, parameters, self.entity_id
                    )
                else:
                    result = session.run(cypher_query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            logger.exception(f"Error executing Neo4j query: {e}")
            logger.exception(f"Query: {cypher_query}")
            logger.exception(f"Parameters: {parameters}")
            raise

    def get_node_by_id(
        self,
        node_id: str,
    ) -> ReferenceSearchResultDTO:
        """
        Retrieve a node by its ID with related inbound and outbound relationships.

        Args:
            node_id: Unique identifier of the node to retrieve

        Returns:
            NodeSearchResultDTO: Data transfer object containing node information

        Raises:
            ValueError: If the node cannot be found
        """

        # Query the database
        params = {"node_id": node_id}
        records = self.query(cypher_query=get_node_by_id_query(), parameters=params)

        if not records:
            raise ValueError(f"Node with id {node_id} not found")

        # Process the query results
        record = records[0]
        node = record["n"]
        labels = record["labels"]

        # Filter relationships to ensure no null values
        outbound_relations = record["outbound_relations"]
        inbound_relations = record["inbound_relations"]
        documentation = record.get("documentation", [])
        workflows = record.get("workflows", [])

        node_info = {
            "node_id": node.get("node_id"),
            "node_name": node.get("name"),
            "file_path": node.get("path"),
            "node_path": node.get("node_path"),
            "start_line": node.get("start_line"),
            "end_line": node.get("end_line"),
            "text": node.get("text"),
            "file_node_id": node.get("file_node_id"),
            "labels": labels,
            "documentation": documentation,
        }

        # Convert to DTO
        node_result = Neo4jNodeSearchResultAdapter.adapt(
            node_data=(node_info, outbound_relations, inbound_relations, workflows)
        )

        return node_result

    def get_node_by_name_and_type(self, name: str, node_type: str) -> list[NodeFoundByNameTypeDto]:
        """
        Retrieve nodes by name and type from the database.

        Args:
            name: Name of the node to search for
            node_type: Type/label of the node to search for
            company_id: Company identifier for data isolation
            repo_id: Repository identifier
            diff_identifier: Diff identifier for version control

        Returns:
            List of NodeFoundByNameTypeDto objects containing node information
        """
        # Query the database
        params = {"name": name, "node_type": node_type}
        records = self.query(cypher_query=get_node_by_name_and_type_query(), parameters=params)

        # Convert records to DTOs
        nodes = []
        for record in records:
            node = NodeFoundByNameTypeDto(
                node_id=record.get("node_id", ""),
                node_name=record.get("node_name", ""),
                node_type=record.get("node_type", []),
                file_path=record.get("file_path", ""),
                code=record.get("code"),
            )
            nodes.append(node)

        return nodes

    def create_function_name_index(self) -> None:
        """Creates a fulltext index on the name and path properties of the nodes."""
        node_query = """
        CREATE FULLTEXT INDEX functionNames IF NOT EXISTS 
        FOR (n:CLASS|FUNCTION|FILE|DIFF) 
        ON EACH [n.name, n.path, n.node_id]
        """
        self.query(node_query)

    def create_node_text_index(self) -> None:
        """Creates a text index on the text property of nodes."""
        node_query = """
        CREATE TEXT INDEX node_text_index IF NOT EXISTS 
        FOR (n:NODE) 
        ON (n.text)
        """
        self.query(node_query)

    def create_node_id_index(self) -> None:
        """Creates an index on node_id for fast lookups."""
        node_query = """
        CREATE INDEX node_id_NODE IF NOT EXISTS 
        FOR (n:NODE) 
        ON (n.node_id)
        """
        self.query(node_query)

    def create_entityId_index(self) -> None:
        """Creates an index on entityId for data isolation."""
        user_query = """
        CREATE INDEX entityId_INDEX IF NOT EXISTS 
        FOR (n:NODE) 
        ON (n.entityId)
        """
        self.query(user_query)

    def create_unique_constraint(self) -> None:
        """Creates a unique constraint for data integrity."""
        constraint_query = """
        CREATE CONSTRAINT user_node_unique IF NOT EXISTS 
        FOR (n:NODE)
        REQUIRE (n.entityId, n.node_id, n.environment) IS UNIQUE
        """
        self.query(constraint_query)

    def create_vector_index(self) -> None:
        """Creates a vector index for semantic search on documentation embeddings."""
        vector_query = """
        CREATE VECTOR INDEX documentation_embeddings IF NOT EXISTS
        FOR (n:NODE)
        ON n.content_embedding
        OPTIONS { indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}
        """
        self.query(vector_query)

    def create_indexes(self) -> None:
        """Create all required indexes for optimal Blarify performance."""
        try:
            self.create_function_name_index()
            # self.create_node_text_index()
            self.create_node_id_index()
            self.create_entityId_index()
            self.create_unique_constraint()
            self.create_vector_index()
            logger.info("Successfully created/verified all Neo4j indexes")
        except Exception as e:
            logger.warning(f"Some indexes may have failed to create: {e}")
