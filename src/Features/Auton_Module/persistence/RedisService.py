from typing import List, Optional
from langchain_redis import RedisVectorStore
from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings
from redisvl.index import SearchIndex
from src.Features.Auton_Module.config.LLMConfig import EmbeddingFactory
from src.infrastructure.Config import Config
from src.SharedKernel.base.Logger import get_logger
from src.SharedKernel.base.Container import Service
from src.SharedKernel.persistence.RedisManager import RedisManager

logger = get_logger(__name__)

config = Config()
config.load_env_yaml()

class IVectorStoreService:
    def add_docs(self, docs: List[Document]):
        ...

    def similarity_search(self, query: str, top_k: int = 4):
        ...

    def as_retriever(self, top_k: int = 5):
        ...

@Service
class RedisService:
    def __init__(self, 
        redis_manager : RedisManager,
    ) -> None:
        self.redis_manager = redis_manager
        self.config        = self.redis_manager.get_redis_config()
        self.vector_store  = self.redis_manager.get_redis_vector_store()
        self.search_index: SearchIndex = self.redis_manager.get_search_index()
        ...

    def add_docs(self, docs: List[Document]):
        return self.vector_store.add_documents(docs)

    def similarity_search(self, query: str, top_k: int = 4):
        return self.vector_store.similarity_search(query, k=top_k)

    def as_retriever(self, top_k: int = 5):
        return self.vector_store.as_retriever(
            search_kwargs={"k": top_k}
        )

    #
    # RAW REDIS
    #
    def cache_set(self, key, value: str, ttl: Optional[int] = None):
        self.redis_manager.cache_set(self.redis_client, key, value, ttl)

    def cache_get(self, key: str):
        return self.redis_manager.cache_get(self.redis_client, key)

    def cache_search(self, query: str):
        def search_func(q):
            docs = self.similarity_search(q)
            return [d.page_content for d in docs]

        return self.redis_manager.cache_search(self.redis_client, query, search_func)