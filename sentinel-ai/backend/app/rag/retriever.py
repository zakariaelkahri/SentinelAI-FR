from app.rag.embeddings import embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

client = QdrantClient(url="http://qdrant:6333")

vectorstore = QdrantVectorStore(
    client=client,
    collection_name="medical_manual",
    embedding=embeddings
)

BASE_RETRIEVER_K = 20
RERANKER_MODEL = "BAAI/bge-reranker-base"
RERANKER_TOP_N = 5

base_retriever = vectorstore.as_retriever(search_kwargs={"k": BASE_RETRIEVER_K})

model = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)

compressor = CrossEncoderReranker(model=model, top_n=RERANKER_TOP_N)

retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# docs = retriever.invoke("What are the duties of a security officer?")
# print(docs)

