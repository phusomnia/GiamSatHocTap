from typing import Optional, Dict, List, Any, Union
from langchain_neo4j import Neo4jVector, GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.language_models import BaseLanguageModel
from src.SharedKernel.base.Logger import get_logger
from src.SharedKernel.base.Container import Singleton
from src.config.Config import Config
from src.Features.Auton_Module.persistence.Neo4jManager import Neo4jManager

logger = get_logger(__name__)
config = Config()
config.load_env_yaml()

@Singleton
class Neo4jVectorManager:
    _instance: Optional['Neo4jVectorManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.neo4j_manager = Neo4jManager()
        self.vector_indexes: Dict[str, Any] = {}
        self.langchain_chains: Dict[str, GraphCypherQAChain] = {}
        self.neo4j_graphs: Dict[str, Neo4jGraph] = {}

    def create_vector_index(
        self,
        index_name: Optional[str] = None,
        node_label: str = "Document",
        embedding_property: str = "embedding",
        dimensions: int = 1536,
        similarity_metric: str = "cosine",
        database: Optional[str] = None
    ) -> bool:
        if index_name is None:
            index_name = config.neo4j.vector_index
        
        query = f"""
        CALL db.index.vector.createNodeIndex(
            '{index_name}',
            '{node_label}',
            '{embedding_property}',
            {dimensions},
            '{similarity_metric}'
        )
        """
        try:
            self.neo4j_manager.execute_write(query, {}, database)
            logger.info(f"Created vector index {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            return False

    def vector_search(
        self,
        query_vector: List[float],
        index_name: Optional[str] = None,
        top_k: int = 5,
        node_label: str = "Document",
        embedding_property: str = "embedding",
        score_threshold: Optional[float] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if index_name is None:
            index_name = config.neo4j.vector_index
        
        query = f"""
        CALL db.index.vector.queryNodes(
            '{index_name}',
            $top_k,
            $query_vector
        ) YIELD node, score
        RETURN node, score, elementId(node) as node_id
        """
        
        if score_threshold is not None:
            query = f"""
            CALL db.index.vector.queryNodes(
                '{index_name}',
                $top_k,
                $query_vector
            ) YIELD node, score
            WHERE score >= $score_threshold
            RETURN node, score, elementId(node) as node_id
            """
        
        params = {
            "query_vector": query_vector,
            "top_k": top_k
        }
        if score_threshold is not None:
            params["score_threshold"] = score_threshold
        
        return self.neo4j_manager.execute_read(query, params, database)

    def add_vector_embedding(
        self,
        node_id: int,
        embedding: List[float],
        embedding_property: str = "embedding",
        database: Optional[str] = None
    ) -> bool:
        query = f"""
        MATCH (n)
        WHERE elementId(n) = $id
        SET n.{embedding_property} = $embedding
        RETURN n
        """
        try:
            self.neo4j_manager.execute_write(query, {"id": str(node_id), "embedding": embedding}, database)
            logger.info(f"Added vector embedding to node {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add vector embedding: {e}")
            return False

    def update_vector_embedding(
        self,
        node_id: int,
        embedding: List[float],
        embedding_property: str = "embedding",
        database: Optional[str] = None
    ) -> bool:
        return self.add_vector_embedding(node_id, embedding, embedding_property, database)

    def delete_vector_index(
        self,
        index_name: Optional[str] = None,
        database: Optional[str] = None
    ) -> bool:
        if index_name is None:
            index_name = config.neo4j.vector_index
        
        query = f"CALL db.index.drop('{index_name}')"
        try:
            self.neo4j_manager.execute_write(query, {}, database)
            logger.info(f"Deleted vector index {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector index: {e}")
            return False

    def get_neo4j_graph(
        self,
        database: Optional[str] = None
    ) -> Neo4jGraph:
        neo4j_url = config.neo4j.url
        username = config.neo4j.username
        password = config.neo4j.password
        db_name = database or config.neo4j.database
        
        graph_key = f"{neo4j_url}:{db_name}"
        if graph_key not in self.neo4j_graphs:
            self.neo4j_graphs[graph_key] = Neo4jGraph(
                url=neo4j_url,
                username=username,
                password=password,
                database=db_name
            )
            logger.info(f"Created Neo4jGraph for {db_name}")
        return self.neo4j_graphs[graph_key]

    def get_graph_cypher_chain(
        self,
        llm: BaseLanguageModel,
        database: Optional[str] = None,
        verbose: bool = False
    ) -> GraphCypherQAChain:
        graph = self.get_neo4j_graph(database)
        chain_key = f"cypher_chain:{database or config.neo4j.database}"
        
        if chain_key not in self.langchain_chains:
            self.langchain_chains[chain_key] = GraphCypherQAChain.from_llm(
                llm=llm,
                graph=graph,
                verbose=verbose,
                allow_dangerous_requests=True
            )
            logger.info(f"Created GraphCypherQAChain for {database or config.neo4j.database}")
        return self.langchain_chains[chain_key]

    def get_neo4j_vector_store(
        self,
        embedding_model: Any,
        index_name: Optional[str] = None,
        node_label: str = "Document",
        embedding_property: str = "embedding",
        text_node_property: str = "text",
        database: Optional[str] = None
    ) -> Neo4jVector:
        if index_name is None:
            index_name = config.neo4j.vector_index
        
        neo4j_url = config.neo4j.url
        username = config.neo4j.username
        password = config.neo4j.password
        db_name = database or config.neo4j.database
        
        store_key = f"vector_store:{index_name}:{db_name}"
        if store_key not in self.vector_indexes:
            self.vector_indexes[store_key] = Neo4jVector.from_existing_graph(
                embedding=embedding_model,
                url=neo4j_url,
                username=username,
                password=password,
                database=db_name,
                index_name=index_name,
                node_label=node_label,
                embedding_node_property=embedding_property,
                text_node_property=text_node_property
            )
            logger.info(f"Created Neo4jVector for {index_name}")
        return self.vector_indexes[store_key]

    def create_knowledge_graph(
        self,
        documents: List[str],
        llm: BaseLanguageModel,
        database: Optional[str] = None
    ) -> bool:
        try:
            graph = self.get_neo4j_graph(database)
            for doc in documents:
                graph.add_document(doc)
            logger.info(f"Created knowledge graph from {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to create knowledge graph: {e}")
            return False
