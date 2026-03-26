from app.rag.chunking import hybrid_chunk
from app.rag.loader import docs
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

documents: list[Document] = []

for source_doc in docs:
    chunks = hybrid_chunk(source_doc.page_content)
    for chunk in chunks:
        metadata = dict(source_doc.metadata)
        metadata.update(chunk.get("metadata", {}))
        documents.append(
            Document(page_content=chunk["content"], metadata=metadata)
        )

if not documents:
    raise ValueError("No documents were generated from the configured RAG source file.")

embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)
