from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from src.Features.Auton_Module.persistence import RedisService
from src.SharedKernel.base.Container import Service
from src.SharedKernel.base.Logger import get_logger
from redisvl.query import TextQuery, VectorQuery
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from ..config.LLMConfig import LLMProviderConfig, EmbeddingProviderConfig
from ..persistence.RedisService import RedisService

logger = get_logger(__name__)

@Service
class Retriever:
    def __init__(self,
        llm_provider: LLMProviderConfig,
        embedding_provider: EmbeddingProviderConfig,
        store_service: RedisService
    ) -> None:
        self.provider = llm_provider.provider
        self.embedding = embedding_provider.embedding
        self.store_service = store_service
        ...

    async def hybrid(self,
        query: str, 
        top_k: 5
    ):
        query_embed = await self.embedding.aembed_query(query)
        logger.info(len(query_embed))

        vector_query = VectorQuery(
            vector=query_embed,
            vector_field_name="embedding",
            num_results=top_k,
            return_fields=["_metadata_json", "text"]
        )

        bm25_query = TextQuery(
            text=query,
            text_field_name="text",
            num_results=top_k,
            return_fields=["_metadata_json", "text"]
        )

        vector_docs = self.store_service.search_index.query(vector_query)
        bm25_docs = self.store_service.search_index.query(bm25_query)
        
        # Combine results using RRF fusion
        fused_docs = self._rff_fusion([vector_docs, bm25_docs], k=60)
        return fused_docs[:top_k]

    def _rff_fusion(self, rank_lists: [], k: int = 60):
        """Simple RRF fusion to combine ranked lists."""
        scores = {}
        doc_map = {}
        
        for rank_list in rank_lists:
            for rank, doc in enumerate(rank_list, 1):
                doc_id = doc.get("id") if isinstance(doc, dict) else getattr(doc, "id", hash(str(doc)))
                scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
                doc_map[doc_id] = doc
        
        return [doc_map[doc_id] for doc_id in sorted(scores, key=scores.get, reverse=True)]

    async def naive(self, query: str):
        _docs = await self.hybrid(query, 5)
        print(_docs)

        retriever = self.store_service.as_retriever(10)
        docs = retriever.invoke(query)
        prompt = PromptTemplate.from_template("""
        Bạn là một trợ lý AI hỗ trợ hãy trả lời câu hỏi dựa vào context dưới đây

        =============
        Context:
        {context}
        =============

        =============
        Question:
        {question}
        =============

        Answer:
        """)

        print(self.format_docs(docs))

        chain = (
            {
                "context": retriever | self.format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.provider
            | StrOutputParser()
        )

        async for chunk in chain.astream(query):
            yield chunk
        ...
        
    def format_docs(self, docs):
        return "".join(f"--- START OF CONTEXT ---\n{doc.page_content}\n--- END OF CONTEXT ---\n\n" for doc in docs)

    async def parent_children(self):
        ...