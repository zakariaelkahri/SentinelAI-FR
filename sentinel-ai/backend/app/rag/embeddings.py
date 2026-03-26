from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.rag.chunking import hybrid_chunk
from app.rag.loader import docs


def build_documents() -> list[Document]:
    built_docs: list[Document] = []

    for source_doc in docs:
        for chunk in hybrid_chunk(source_doc.page_content):
            metadata = {**source_doc.metadata, **chunk.get("metadata", {})}
            built_docs.append(Document(page_content=chunk["content"], metadata=metadata))

    if not built_docs:
        raise ValueError("No documents were generated from the configured RAG source file.")

    return built_docs


documents = build_documents()
embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
