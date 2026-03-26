from app.core.config import settings
from app.rag.embeddings import documents, embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


client = QdrantClient(url=settings.QDRANT_URL)

try:
    client.delete_collection(collection_name="medical_manual")
    print("Deleted existing collection")
except Exception as e:
    print(f"No collection to delete: {e}")

vectorstore = QdrantVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    url=settings.QDRANT_URL,
    collection_name="medical_manual"
)
