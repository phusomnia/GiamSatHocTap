from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from src.SharedKernel.base.Container import Service

@Service
class ProcessService:
    def __init__(self) -> None:
        ...

    def chunking(self, 
        chunk_size: int,
        chunk_overlap: int, 
        docs: List[Document]
    ):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        result = splitter.split_documents(docs)

        self.find_pages_span(splitter, docs)
        # for i in range(min(50, len(docs))):
        #     print(f"Chunk {i}: span_page={docs[i].metadata}\nText: {docs[i].page_content}\n")

        return result

    def ParentChild_chunking(
        self,
        parent_chunk_size: int = 1000,
        parent_chunk_overlap: int = 100,
        children_chunk_size: int = 512,
        children_chunk_overlap: int = 200,
    ): 
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap
        )

        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50
        )


    def split_orginal_text_into_pages(self, full_text: str):
        pages = full_text.split("<<PAGE_BREAK>>")
        return self.build_page_map(pages)

    def build_page_map(self, pages):
        """
        Build page offset
        """
        page_offsets = []

        cursor = 0

        for page_number, page_text in enumerate(pages):

            start = cursor
            end = start + len(page_text)

            page_offsets.append({
                "page": page_number + 1,
                "start": start,
                "end": end
            })

            cursor = end + len("<<PAGE_BREAK>>")

        return page_offsets

    def find_pages_span(self, splitter, docs):
        
        full_text = ""
        for doc in docs:
            full_text += doc.page_content
        
        chunks = splitter.split_text(full_text)
        # print(chunks)
        # page_offsets = self.split_orginal_text_into_pages(full_text)
        
        # documents = []

        # search_cursor = 0

        # for chunk_id, chunk_text in enumerate(chunks):
        #     chunk_start = full_text.find(chunk_text, search_cursor)
            
        #     chunk_end = chunk_start + len(chunk_text)

        #     search_cursor = chunk_start

        #     page_start = None
        #     page_end = None

        #     for page_info in page_offsets:
        #         page = page_info["page"]
        #         start = page_info["start"]
        #         end = page_info["end"]

        #         if start <= chunk_start <= end:
        #             page_start = page
                
        #         if start <= chunk_end <= end:
        #             page_end = page

        #     span_page = [page_start, page_end]

        #     documents.append(Document(
        #         page_content=chunk_text,
        #         metadata={
        #             "chunk_id"    : chunk_id,
        #             "chunk_start" : chunk_start,
        #             "chunk_end"   : chunk_end,
        #             "span_page"   : span_page,
        #             "source"      : ".pdf",
        #         }
        #     ))

        # return documents
        ...