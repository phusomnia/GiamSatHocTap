from typing import Optional, Dict
from langchain.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from redis import Redis, ConnectionPool
from redisvl import index
from redisvl.index import SearchIndex
from langchain_community.storage.redis import RedisStore
from langchain_redis import RedisConfig, RedisVectorStore
from src.SharedKernel.base.Logger import get_logger, ILogger
from src.SharedKernel.base.Container import Singleton
from src.Infrastructure.Config import Config
from src.Features.Auton_Module.config.LLMConfig import EmbeddingProviderConfig
import os

config = Config()
config.load_env_yaml()

@Singleton
class RedisManager:
    _instance: Optional['RedisManager'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, 
        log: ILogger, 
        embedding_provider: EmbeddingProviderConfig
    ):
        if self._initialized:
            return
        self._initialized = True

        self.pools   : Dict[str, ConnectionPool] = {}
        self.clients : Dict[str, Redis]          = {}
        self.configs : Dict[str, RedisConfig]    = {}
        self.indexes : Dict[str, SearchIndex]    = {}
        self.stores  : Dict[str, RedisStore]     = {}

        self.vector_store : Dict[str, RedisVectorStore] = {} 

        self.embedding = embedding_provider.embedding
        self.logger = log

    ### GETTER ###
    def get_redis_client(self) -> Redis:
        redis_url = config.redis.url
        if redis_url not in self.clients:
            self.clients[redis_url] = Redis.from_url(redis_url)
            self.logger.info(f"Created Redis client for {redis_url}")
        return self.clients[redis_url]

    def get_redis_config(self,) -> RedisConfig:
        self.logger.info("Starting get_redis_config...")
        redis_url = config.redis.url
        index_name = config.redis.index_name
        distance_metric = "COSINE"
        config_key = f"{index_name}:{redis_url}"
        if config_key not in self.configs:
            self.logger.info(f"Creating new RedisConfig for {index_name}")
            self.configs[config_key] = RedisConfig(
                redis_url=redis_url,
                index_name=index_name,
                distance_metric=distance_metric
            )
            self.logger.info(f"Created RedisConfig for {index_name}")
        else:
            self.logger.info(f"Using existing RedisConfig for {index_name}")
        return self.configs[config_key]

    def get_redis_vector_store(self):
        self.logger.info("Starting get_redis_vector_store...")
        redis_config = self.get_redis_config()
        redis_url = config.redis.url
        index_name = config.redis.index_name
        store_key = f"{index_name}:{redis_url}"

        if store_key not in self.vector_store:
            # Skip RedisVectorStore creation on Windows to prevent hanging
            import platform
            if platform.system() == "Windows":
                self.logger.warning("Windows detected: Skipping RedisVectorStore creation to prevent hanging")
                return None

            self.logger.info(f"Creating new RedisVectorStore for {store_key}")
            self.logger.info("About to access embedding property...")
            self.vector_store[store_key] = RedisVectorStore(
                embeddings=self.embedding,
                config=redis_config
            )
            self.logger.info(f"Created RedisVectorStore for {store_key}")
        else:
            self.logger.info(f"Using existing RedisVectorStore for {store_key}")

        return self.vector_store[store_key]
        ... 

    def get_search_index(self):
        self.logger.info("Starting get_search_index...")
        redis_url = config.redis.url
        index_name = config.redis.index_name
        index_key  = f"{index_name}:{redis_url}"

        if index_key not in self.indexes:
            # Skip SearchIndex creation on Windows to prevent hanging
            import platform
            if platform.system() == "Windows":
                self.logger.warning("Windows detected: Skipping SearchIndex creation to prevent hanging")
                self.indexes[index_key] = None
                return self.indexes[index_key]

            try:
                os.environ["REDIS_URL"] = redis_url
                # Load SearchIndex from YAML file
                index_yaml_path = "src/config/index.yaml"
                self.logger.info(f"Loading SearchIndex from {index_yaml_path}...")
                self.indexes[index_key] = SearchIndex.from_yaml(index_yaml_path)
                self.logger.info(":D X - SearchIndex loaded from YAML successfully")
            except Exception as e:
                self.logger.warning(f"Failed to load SearchIndex from YAML: {e}")
                self.indexes[index_key] = None

        return self.indexes[index_key]
        ...
    ###
    def create_connection_pool(self, 
        redis_url: str, 
        max_connections: int = 10
    ) -> ConnectionPool:
        if redis_url not in self.pools:
            self.pools[redis_url] = ConnectionPool.from_url(
                redis_url,
                max_connections=max_connections
            )
            self.logger.info(f"Created connection pool for {redis_url}")
        return self.pools[redis_url]

    def get_or_create_pool(self, 
        redis_url: str, 
        max_connections: int = 10
    ) -> ConnectionPool:
        return self.create_connection_pool(
            redis_url, 
            max_connections
        )

    def cache_set(self, 
        redis_client: Redis, 
        key: str, 
        value: str, 
        ttl: Optional[int] = None
    ):
        if ttl:
            redis_client.setex(key, ttl, value)
        else:
            redis_client.set(key, value)
        self.logger.info(f"SET cache: {key}")

    def cache_get(self, 
        redis_client: Redis, 
        key: str
    ) -> Optional[str]:
        self.logger.info(f"GET cache: {key}")
        result = redis_client.get(key)
        return result.decode('utf-8') if result else None

    def cache_search(self, 
        redis_client: Redis, 
        query: str, 
        search_func
    ):
        cache_key = f"search:{query}"

        cached = self.cache_get(redis_client, cache_key)
        if cached:
            self.logger.info("⚡ Cache hit")
            return cached

        result = search_func(query)
        self.cache_set(redis_client, cache_key, str(result))

        return result

    def health_check(self, redis_url: str) -> bool:
        try:
            client = self.get_redis_client(redis_url)
            client.ping()
            self.logger.info(f"Redis health check passed for {redis_url}")
            return True
        except Exception as e:
            self.logger.error(f"Redis health check failed for {redis_url}: {e}")
            return False

    def close_all_connections(self):
        for pool in self.pools.values():
            pool.disconnect()
        for client in self.clients.values():
            client.close()
        self.pools.clear()
        self.clients.clear()
        self.logger.info("All Redis connections closed")