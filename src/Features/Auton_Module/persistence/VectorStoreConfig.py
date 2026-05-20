# from abc import ABC, abstractmethod
# from typing import TypeVar
# from langchain.embeddings import Embeddings
# from langchain_core.vectorstores import InMemoryVectorStore
# from enum import Enum
# from langchain_community.vectorstores import FAISS

# class VectorStoreProvider(Enum):
#     INMEM = 'inmem'
#     FAISS = 'faiss'
#     REDIS = 'redis'

# class BaseVectorStoreProvider(ABC):
#     @abstractmethod
#     def get_store(self, embbeding: Embeddings):
#         ...

# class InMemProvider(BaseVectorStoreProvider):
#     def __init__(self) -> None:
#         self.vstore = None
        
#     def get_vstore(self, embbeding: Embeddings): 
#         return InMemoryVectorStore(embbeding)

# class FaissProvider(BaseVectorStoreProvider):
#     def __init__(self) -> None:
#         self.vstore = None

#     def get_store(self, embbeding: Embeddings):
#         return FAISS.from_documents([], embedding=embbeding)

# T = TypeVar('T')

# class RegistryProvider(Generic[T]):
#     def __init__(self):
#         self._providers: Dict[str, Type[T]] = {}
 
#     def register(self, name: str, provider: Type[T]):
#         self._providers[name] = provider
 
#     def get_provider(self, name: str) -> Type[T]:
#         provider = self._providers.get(name)
#         if not provider: 
#             raise HTTPException(f"Provider {name} is not found")
#         return provider

# class VectorStoreFactory():
#     @staticmethod
#     def create(provider_name: str, embbeding: Embeddings):
#         provider_cls = vstore_registry.get_provider(provider_name)
#         return provider_cls().get_store(embedding)
        
# vstore_registry = ProviderRegistry[BaseVectorStoreProvider]()
# vstore_registry.register(VectorStoreProvider.INMEM.value, InMemProvider)