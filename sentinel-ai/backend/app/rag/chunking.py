from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)

from app.core.config import settings


def hybrid_chunk(text: str):
    md_splitter = MarkdownHeaderTextSplitter([
        ("#", "Chapter"),
        ("##", "Section"),
        ("###", "Subsection"),
    ])

    structured_docs = md_splitter.split_text(text)

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    final_chunks = []

    for doc in structured_docs:
        sub_chunks = recursive_splitter.split_text(doc.page_content)

        for chunk in sub_chunks:
            final_chunks.append({
                "content": chunk,
                "metadata": doc.metadata
            })

    return final_chunks
