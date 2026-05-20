import os
import shutil
import tempfile
from enum import Enum
from fastapi import File, HTTPException
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader, UnstructuredWordDocumentLoader
from typing import Callable, Dict, List
from src.SharedKernel.base.Container import Service
from src.SharedKernel.base.Logger import ILogger


class FileExtensionState(Enum):
    PDF = "pdf"
    TEXT = "text"
    CSV = "csv"
    WORD = "word"
    EXCEL = "excel"
    UNSUPPORTED = "unsupported"

@Service
class LoaderService:
    def __init__(self, 
        logger: ILogger,
    ) -> None:
        self.extension_state: Dict[str, FileExtensionState] = {
            '.pdf': FileExtensionState.PDF,
            '.txt': FileExtensionState.TEXT,
            '.md': FileExtensionState.TEXT,
            '.doc': FileExtensionState.WORD,
            '.docx': FileExtensionState.WORD,
        }

        self.state_loader: Dict[FileExtensionState, Callable] = {
            FileExtensionState.PDF  : self.load_pdf,
            FileExtensionState.TEXT : self.load_text,
            FileExtensionState.WORD : self.load_docx
        }

        self.logger = logger
        ...

    def load_file(self, file: File):
        # Detect file
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        state = self.extension_state.get(ext, FileExtensionState.UNSUPPORTED)

        if state == FileExtensionState.UNSUPPORTED:
            raise HTTPException(400, "Unsupported file")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
            ...

        file_size_kb = os.path.getsize(temp_path) / 1024
        suffix = os.path.splitext(file.filename)[1].upper()
        path = os.path.basename(temp_path)

        self.logger.info(
            f"kb: {file_size_kb}" +
            f"suffix: {suffix}" +
            f"path: {path}"
        )

        try:
            loader_func = self.state_loader[state]
            docs = loader_func(temp_path)
            for doc in docs:
                doc.metadata['source'] = filename
            return docs
        finally:
            os.unlink(temp_path)

    def load_pdf(self, path: str):
        loader = PyPDFLoader(
            path, 
            mode="single",
            pages_delimiter="\n<<PAGE_BREAK>>\n"
        )

        docs = loader.load()

        return docs

    def load_text(self, path: str):
        loader = TextLoader(path)
        docs = loader.load() 
        return docs

    def load_docx(self, path: str):
        loader = UnstructuredWordDocumentLoader(path)
        docs = loader.load()
        return docs

    def load_web(self, url: str) -> List[Document]:
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs
    ...