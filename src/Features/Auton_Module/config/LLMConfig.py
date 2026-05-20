from abc import abstractmethod, ABC
from http.client import HTTPException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.embeddings import Embeddings
from src.SharedKernel import base
from src.SharedKernel.base.Container import Configuration
from src.config.Config import Config
from typing import TypeVar, Generic, Dict, Type
from enum import Enum

config = Config()
config.load_env_yaml()

T = TypeVar('T')

class Provider(Enum): 
    OLLAMA = 'ollama'
    MISTRAL = 'mistral'
    GROK = 'grok'

# ==============================
# BASE PROVIDERS
# ==============================
class BaseLLMProvider(ABC):
    @abstractmethod
    def get_llm(self) -> BaseChatModel:
        ...

class BaseEmbeddingProvider(ABC):    
    @abstractmethod
    def get_embedding(self) -> Embeddings:
        ...

#
# PROVIDERS
# 
class OllamaLLMProvider(BaseLLMProvider):
    def get_llm(self) -> BaseChatModel:
        options = vars(config.llm.ollama.options) if hasattr(config.llm.ollama, 'options') else {}
        provider = ChatOllama(
            model=config.llm.ollama.model,
            base_url=config.llm.ollama.base_url,
            **options
        )
        print(provider)
        return provider


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    def get_embedding(self) -> Embeddings:
        return OllamaEmbeddings(
            model=config.llm.ollama.embedding,
            base_url=config.llm.ollama.base_url
        )

class ProviderRegistry(Generic[T]):
    def __init__(self):
        self._providers: Dict[str, Type[T]] = {}

    def register(self, name: str, provider: Type[T]):
        self._providers[name] = provider
        
    def get_provider(self, name: str) -> Type[T]:
        provider = self._providers.get(name)
        if not provider: 
            raise HTTPException(f"Provider {name} is not found")
        return provider
llm_registry = ProviderRegistry[BaseLLMProvider]()
embedding_registry = ProviderRegistry[BaseEmbeddingProvider]()

llm_registry.register(Provider.OLLAMA.value, OllamaLLMProvider)
embedding_registry.register(Provider.OLLAMA.value, OllamaEmbeddingProvider)

class LLMFactory:
    @staticmethod
    def create(provider_name: str) -> BaseChatModel:
        provider_cls = llm_registry.get_provider(provider_name)
        return provider_cls().get_llm()
        
class EmbeddingFactory:
    @staticmethod
    def create(provider_name: str) -> Embeddings:
        provider_cls = embedding_registry.get_provider(provider_name)
        return provider_cls().get_embedding()

@Configuration
class LLMProviderConfig:
    def __init__(self):
        self._provider = LLMFactory.create(config.llm.provider)
    
    @property
    def provider(self) -> BaseChatModel:
        return self._provider

@Configuration
class EmbeddingProviderConfig:
    def __init__(self):
        self._embedding = EmbeddingFactory.create(config.llm.provider)
    
    @property
    def embedding(self) -> Embeddings:
        return self._embedding

