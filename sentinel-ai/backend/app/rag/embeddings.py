from app.rag.chunking import hybrid_chunk
from app.rag.loader import docs
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

md_text = docs[0].page_content
chunks = hybrid_chunk(md_text)

documents = [
    Document(page_content=chunk["content"], metadata=chunk.get("metadata", {}))
    for chunk in chunks
]

embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)
