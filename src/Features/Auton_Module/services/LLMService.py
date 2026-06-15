from abc import abstractmethod, ABC
import shutil
import tempfile
import os
from fastapi import File, HTTPException, UploadFile
from langchain_core.callbacks.stdout import StdOutCallbackHandler
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Callable, List
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from enum import Enum

from ollama import generate
from redis import Redis
from sqlalchemy.util import generic_repr
from src.Features.Auton_Module.services.Retriever import Retriever
from src.SharedKernel.base.Container import Service
from src.infrastructure.Config import Config

from .LoaderService import LoaderService
from .ProcessService import ProcessService
from ..persistence.RedisService import RedisService
from ..config.LLMConfig import LLMProviderConfig, EmbeddingProviderConfig

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.SharedKernel.base import Metrics

import json
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_vector_index, upsert_vectors
from neo4j_graphrag.types import EntityType
from langchain_ollama import OllamaEmbeddings, ChatOllama

# from langchain_core.globals import set_debug
# set_debug(True)

config = Config()
config.load_env_yaml()
config.load_prompts()

class BaseRAG(ABC):    
    @abstractmethod
    def indexing(self):
        ...
    
    @abstractmethod
    def augmenting(self):
        ...

@Service
class RAG(BaseRAG):
    def __init__(
        self,
        llm_provider: LLMProviderConfig,
        embedding_provider: EmbeddingProviderConfig,
        loader_service: LoaderService,
        store_service: RedisService,
        process_service: ProcessService,
        retriever: Retriever,
    ) -> None:
        super().__init__()
        self.provider = llm_provider.provider
        self.embedding = embedding_provider.embedding

        self.loader_service = loader_service
        self.process_service = process_service

        self.store_service = store_service        
        self.retriever = retriever
        ...

    @Metrics.time_function
    def indexing(self, files: List[UploadFile]):
        for file in files:
            docs = self.loader_service.load_file(file)

            if not docs: 
                raise HTTPException(500, "Loader thất bại")

            chunks = self.process_service.chunking(
                512, 
                100, 
                docs
            )        
            print(f"Length of chunk: {len(chunks)}")

            # self.store_service.add_docs(chunks)
        ...

    @Metrics.time_function
    async def augmenting(self, 
        session_id: str, 
        query: str
    ):
        async for chunk in self.retriever.naive(query):
            yield chunk

@Service
class GraphRAG:
    def __init__(
        self
    ) -> None:
        ...

    @Metrics.time_function
    def indexing(self):
        URI = "neo4j://localhost:7687"
        AUTH = ("neo4j", "12345678")

        driver = GraphDatabase.driver(URI, auth=AUTH)

        documents = [
            "GraphRAG combines graph databases and vector search to enhance retrieval augmented generation. Neo4j is a popular graph database used in GraphRAG implementations. LangChain provides orchestration framework for building GraphRAG applications.",
            "Neo4j stores data in nodes and relationships, making it ideal for knowledge graphs. Neo4j connects to vector databases like Pinecone for hybrid search. Developers use Neo4j with LangChain to build RAG systems.",
            "LangChain integrates with various vector stores and databases. LangChain supports Neo4j as a graph store and works with embedding models. LangChain orchestrates the entire RAG pipeline from document processing to answer generation."
        ]

        # LLM EXTRACTION ENTITIES + RELATIONS
        llm = ChatOllama(
            model="qwen3-vl:4b-instruct"
        )

        def create_nodes():
            with driver.session() as s:
                for i, docs in enumerate(documents):
                    s.run(
                        """
                        CREATE (n:Document {id: $id, text: $text})
                        """,
                        id=f"doc{i}",
                        text=docs,
                    )

        def create_index():
            create_vector_index(
                driver,
                "doc_index",
                label="Document",
                embedding_property="embedding",
                dimensions=768,
                similarity_fn="cosine"
            )

        def generate_embed():
            embedder = OllamaEmbeddings(model="nomic-embed-text:latest")
            embedding = embedder.embed_documents(documents)
            return embedding

        def insert_embedding():
            upsert_vectors(
                driver,
                ids=[f"doc{i}" for i in range(len(documents))],
                embedding_property="embedding",
                embeddings=generate_embed(),
                entity_type=EntityType.NODE,
            )

        def extract_graph(text):
            prompt = f"""
                Extract entities and relationships from text.

                Return ONKY valid JSON

                Format: 
                {{
                    "entities": [
                        {{
                            "name": "...",
                            "type": "Technology"
                        }}
                    ],
                    "relationships": [
                        {{
                        "source": "...",
                        "target": "...",
                        "type": "RELATED_TO"
                        }}
                    ]
                }}

                Text:
                {text}
                """
            response = llm.invoke(prompt)
            content = response.content
            
            return json.loads(content)
        
        def create_graph():
            with driver.session() as s:
                for i, doc in enumerate(documents):
                    graph = extract_graph(doc)
                    
                    entities = graph["entities"]
                    relationships = graph["relationships"]

                    print(graph)
                
                    for entity in entities:
                        s.run(
                            f"""
                                MERGE (e:Entity {{
                                    name: $name
                                }})
                                SET e.type = $type
                            """,
                            name=entity["name"],
                            type=entity["type"]
                        )

                        s.run(
                            f"""
                            MATCH (d:DOCUMENT {{id:$doc_id}})
                            MATCH (e:Entity {{name:$name}})

                            MERGE (d)-[:MENTIONS]->(e)
                            """,
                            doc_id=f"doc{i}",
                            name=entity["name"]
                        )

                    for rel in relationships:
                        cypher = f"""
                        MATCH (a:Entity {{name:$source}})
                        MATCH (b:Entity {{name:$target}})

                        MERGE (a)-[r:{rel['type']}]->(b)
                        """

                        s.run(
                            cypher,
                            source=rel["source"],
                            target=rel["target"]
                        )
                ...

        create_nodes()
        create_index()
        generate_embed()
        insert_embedding()
        create_graph()

        print("Data ingest")

    @Metrics.time_function
    def retrieve():
        print("retrieve")

        
        ...

@Service
class LLMService:
    def __init__(self,
        llm_provider: LLMProviderConfig,
        embedding_provider: EmbeddingProviderConfig,
        naive_rag: RAG,
        graph_rag: GraphRAG,
    ) -> None:
        self.provider = llm_provider.provider
        self.embedding = embedding_provider.embedding
        self.naive_rag = naive_rag
        self.graph_rag = graph_rag
        print(f"{self.provider}\n{self.embedding}")
        ...

    async def prompt(self, query: str):
        return await self.provider.ainvoke(query)

    async def sprompt(self, query: str):
        query = config.SYSTEM_PROMPT + query
        print(query)
        async for chunk in self.provider.astream(query):
            yield chunk.content
        ...