from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.rag.schemas import Chunk, ChunkMetadata

HEADERS = [("#", "h1"), ("##", "h2")]


def split_markdown(text: str, source: str) -> list[Chunk]:
    header_splitter = MarkdownHeaderTextSplitter(HEADERS)
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents = size_splitter.split_documents(header_splitter.split_text(text))

    chunks: list[Chunk] = []

    for doc in documents:
        title = doc.metadata.get("h1", Path(source).stem)
        section = doc.metadata.get("h2", "Введение")

        chunks.append(
            Chunk(
                page_content=f"{title} → {section}\n\n{doc.page_content}",
                metadata=ChunkMetadata(
                    source=source,
                    title=title,
                    section=section,
                )
            )
        )

    return chunks
