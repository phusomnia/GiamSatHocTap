from typing import Optional, Dict, List, Any, Union
from neo4j import GraphDatabase, Driver, Session, Result
from src.SharedKernel.base.Logger import get_logger
from src.SharedKernel.base.Container import Singleton
from src.config.Config import Config

logger = get_logger(__name__)
config = Config()
config.load_env_yaml()

@Singleton
class Neo4jManager:
    _instance: Optional['Neo4jManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.drivers: Dict[str, Driver] = {}
        self.sessions: Dict[str, Session] = {}

    def get_driver(self) -> Driver:
        neo4j_url = config.neo4j.url
        username = config.neo4j.username
        password = config.neo4j.password
        database = config.neo4j.database
        
        driver_key = f"{neo4j_url}:{database}"
        if driver_key not in self.drivers:
            self.drivers[driver_key] = GraphDatabase.driver(
                neo4j_url,
                auth=(username, password)
            )
            logger.info(f"Created Neo4j driver for {neo4j_url}")
        return self.drivers[driver_key]

    def get_session(self, database: Optional[str] = None) -> Session:
        if database is None:
            database = config.neo4j.database
        
        neo4j_url = config.neo4j.url
        session_key = f"{neo4j_url}:{database}"
        
        if session_key not in self.sessions:
            driver = self.get_driver()
            self.sessions[session_key] = driver.session(database=database)
            logger.info(f"Created Neo4j session for database {database}")
        return self.sessions[session_key]

    def close_all_connections(self):
        for session in self.sessions.values():
            session.close()
        for driver in self.drivers.values():
            driver.close()
        self.sessions.clear()
        self.drivers.clear()
        logger.info("All Neo4j connections closed")

    def health_check(self) -> bool:
        try:
            driver = self.get_driver()
            driver.verify_connectivity()
            logger.info("Neo4j health check passed")
            return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        session = self.get_session(database)
        try:
            result = session.run(query, parameters or {})
            records = [record.data() for record in result]
            logger.info(f"Executed query: {query[:100]}...")
            return records
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            result.consume() if 'result' in locals() else None

    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        session = self.get_session(database)
        try:
            result = session.execute_write(lambda tx: tx.run(query, parameters or {}))
            records = [record.data() for record in result]
            logger.info(f"Executed write query: {query[:100]}...")
            return records
        except Exception as e:
            logger.error(f"Write query execution failed: {e}")
            raise

    def execute_read(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        session = self.get_session(database)
        try:
            result = session.execute_read(lambda tx: tx.run(query, parameters or {}))
            records = [record.data() for record in result]
            logger.info(f"Executed read query: {query[:100]}...")
            return records
        except Exception as e:
            logger.error(f"Read query execution failed: {e}")
            raise

    def batch_execute(
        self,
        queries: List[str],
        parameters_list: Optional[List[Dict[str, Any]]] = None,
        database: Optional[str] = None
    ) -> List[List[Dict[str, Any]]]:
        session = self.get_session(database)
        results = []
        try:
            for i, query in enumerate(queries):
                params = parameters_list[i] if parameters_list and i < len(parameters_list) else None
                result = session.run(query, params or {})
                records = [record.data() for record in result]
                results.append(records)
                result.consume()
            logger.info(f"Executed {len(queries)} queries in batch")
            return results
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise

    def create_node(
        self,
        labels: Union[str, List[str]],
        properties: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        if isinstance(labels, str):
            labels = [labels]
        
        label_str = ":".join(labels)
        query = f"CREATE (n:{label_str} $props) RETURN n"
        result = self.execute_write(query, {"props": properties or {}}, database)
        return result[0] if result else {}

    def update_node(
        self,
        node_id: int,
        properties: Dict[str, Any],
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        query = "MATCH (n) WHERE elementId(n) = $id SET n += $props RETURN n"
        result = self.execute_write(query, {"id": str(node_id), "props": properties}, database)
        return result[0] if result else {}

    def delete_node(
        self,
        node_id: int,
        database: Optional[str] = None
    ) -> bool:
        query = "MATCH (n) WHERE elementId(n) = $id DETACH DELETE n"
        self.execute_write(query, {"id": str(node_id)}, database)
        logger.info(f"Deleted node {node_id}")
        return True

    def get_node(
        self,
        node_id: int,
        database: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        query = "MATCH (n) WHERE elementId(n) = $id RETURN n"
        result = self.execute_read(query, {"id": str(node_id)}, database)
        return result[0] if result else None

    def create_relationship(
        self,
        from_node_id: int,
        to_node_id: int,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        query = f"""
        MATCH (a), (b)
        WHERE elementId(a) = $from_id AND elementId(b) = $to_id
        CREATE (a)-[r:{relationship_type} $props]->(b)
        RETURN r
        """
        result = self.execute_write(
            query,
            {"from_id": str(from_node_id), "to_id": str(to_node_id), "props": properties or {}},
            database
        )
        return result[0] if result else {}

    def update_relationship(
        self,
        relationship_id: int,
        properties: Dict[str, Any],
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        query = "MATCH ()-[r]->() WHERE elementId(r) = $id SET r += $props RETURN r"
        result = self.execute_write(query, {"id": str(relationship_id), "props": properties}, database)
        return result[0] if result else {}

    def delete_relationship(
        self,
        relationship_id: int,
        database: Optional[str] = None
    ) -> bool:
        query = "MATCH ()-[r]->() WHERE elementId(r) = $id DELETE r"
        self.execute_write(query, {"id": str(relationship_id)}, database)
        logger.info(f"Deleted relationship {relationship_id}")
        return True

    def get_relationships(
        self,
        node_id: int,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if direction == "outgoing":
            pattern = "(n)-[r]->(m)"
        elif direction == "incoming":
            pattern = "(n)<-[r]-(m)"
        else:
            pattern = "(n)-[r]-(m)"
        
        type_filter = f":{relationship_type}" if relationship_type else ""
        query = f"""
        MATCH {pattern}{type_filter}
        WHERE elementId(n) = $id
        RETURN r, elementId(r) as rel_id, type(r) as rel_type
        """
        return self.execute_read(query, {"id": str(node_id)}, database)

    def traverse(
        self,
        start_node_id: int,
        max_depth: int = 3,
        relationship_types: Optional[List[str]] = None,
        direction: str = "outgoing",
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if direction == "outgoing":
            pattern = "(start)-[r*1..{max_depth}]->(end)"
        elif direction == "incoming":
            pattern = "(start)<-[r*1..{max_depth}]-(end)"
        else:
            pattern = "(start)-[r*1..{max_depth}]-(end)"
        
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_filter = f":{rel_types}"
        
        query = f"""
        MATCH (start), {pattern.replace('{max_depth}', str(max_depth))}{rel_filter}
        WHERE elementId(start) = $start_id
        RETURN start, r, end, elementId(end) as end_id
        """
        return self.execute_read(query, {"start_id": str(start_node_id)}, database)

    def find_shortest_path(
        self,
        from_node_id: int,
        to_node_id: int,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 10,
        database: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_filter = f":{rel_types}"
        
        query = f"""
        MATCH (a), (b), path = shortestPath((a)-[r*1..{max_depth}{rel_filter}]->(b))
        WHERE elementId(a) = $from_id AND elementId(b) = $to_id
        RETURN path, length(path) as path_length
        """
        result = self.execute_read(query, {"from_id": str(from_node_id), "to_id": str(to_node_id)}, database)
        return result[0] if result else None

    def get_neighbors(
        self,
        node_id: int,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if direction == "outgoing":
            pattern = "(n)-[r]->(neighbor)"
        elif direction == "incoming":
            pattern = "(n)<-[r]-(neighbor)"
        else:
            pattern = "(n)-[r]-(neighbor)"
        
        type_filter = f":{relationship_type}" if relationship_type else ""
        query = f"""
        MATCH {pattern}{type_filter}
        WHERE elementId(n) = $id
        RETURN neighbor, elementId(neighbor) as neighbor_id, labels(neighbor) as labels
        """
        return self.execute_read(query, {"id": str(node_id)}, database)

    def find_connected_components(
        self,
        label: Optional[str] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        label_filter = f":{label}" if label else ""
        query = f"""
        MATCH (n{label_filter})
        WITH n, [rel IN [(n)-[r]-(m) | m] WHERE elementId(m) <> elementId(n)] as neighbors
        RETURN n, neighbors, elementId(n) as node_id
        """
        return self.execute_read(query, {}, database)

    def bfs_traversal(
        self,
        start_node_id: int,
        max_depth: int = 3,
        relationship_type: Optional[str] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        type_filter = f":{relationship_type}" if relationship_type else ""
        query = f"""
        MATCH (start)
        WHERE elementId(start) = $start_id
        CALL apoc.path.subgraphAll(start, {
            maxLevel: $max_depth,
            relationshipFilter: '{type_filter if type_filter else ''}'
        })
        YIELD nodes, relationships
        RETURN nodes, relationships
        """
        try:
            return self.execute_read(query, {"start_id": str(start_node_id), "max_depth": max_depth}, database)
        except Exception:
            logger.warning("APOC not available, using alternative BFS traversal")
            return self.traverse(start_node_id, max_depth, [relationship_type] if relationship_type else None, "outgoing", database)

    def dfs_traversal(
        self,
        start_node_id: int,
        max_depth: int = 3,
        relationship_type: Optional[str] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        type_filter = f":{relationship_type}" if relationship_type else ""
        query = f"""
        MATCH (start)
        WHERE elementId(start) = $start_id
        CALL apoc.path.spanningTree(start, {
            maxLevel: $max_depth,
            relationshipFilter: '{type_filter if type_filter else ''}'
        })
        YIELD path
        RETURN path
        """
        try:
            return self.execute_read(query, {"start_id": str(start_node_id), "max_depth": max_depth}, database)
        except Exception:
            logger.warning("APOC not available, using alternative DFS traversal")
            return self.traverse(start_node_id, max_depth, [relationship_type] if relationship_type else None, "outgoing", database)

    def create_constraint(
        self,
        constraint_name: str,
        label: str,
        property_name: str,
        constraint_type: str = "unique",
        database: Optional[str] = None
    ) -> bool:
        if constraint_type == "unique":
            query = f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
            FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE
            """
        elif constraint_type == "exists":
            query = f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
            FOR (n:{label}) REQUIRE n.{property_name} IS NOT NULL
            """
        else:
            logger.error(f"Unsupported constraint type: {constraint_type}")
            return False
        
        try:
            self.execute_write(query, {}, database)
            logger.info(f"Created {constraint_type} constraint {constraint_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create constraint: {e}")
            return False

    def create_index(
        self,
        index_name: str,
        label: str,
        property_names: Union[str, List[str]],
        database: Optional[str] = None
    ) -> bool:
        if isinstance(property_names, str):
            property_names = [property_names]
        
        props_str = ", ".join([f"n.{prop}" for prop in property_names])
        query = f"""
        CREATE INDEX {index_name} IF NOT EXISTS
        FOR (n:{label}) ON ({props_str})
        """
        
        try:
            self.execute_write(query, {}, database)
            logger.info(f"Created index {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def get_schema(self, database: Optional[str] = None) -> Dict[str, Any]:
        query = """
        CALL db.schema.visualization()
        YIELD nodes, relationships
        RETURN nodes, relationships
        """
        result = self.execute_read(query, {}, database)
        return result[0] if result else {"nodes": [], "relationships": []}

    def drop_constraint(
        self,
        constraint_name: str,
        database: Optional[str] = None
    ) -> bool:
        query = f"DROP CONSTRAINT {constraint_name} IF EXISTS"
        try:
            self.execute_write(query, {}, database)
            logger.info(f"Dropped constraint {constraint_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to drop constraint: {e}")
            return False

    def drop_index(
        self,
        index_name: str,
        database: Optional[str] = None
    ) -> bool:
        query = f"DROP INDEX {index_name} IF EXISTS"
        try:
            self.execute_write(query, {}, database)
            logger.info(f"Dropped index {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to drop index: {e}")
            return False

    def clear_database(self, database: Optional[str] = None) -> bool:
        query = "MATCH (n) DETACH DELETE n"
        try:
            self.execute_write(query, {}, database)
            logger.warning("Database cleared - all nodes and relationships deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return False