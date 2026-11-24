import pytest

from app.rag.schemas import Chunk, ChunkMetadata


async def make_chunk(source: str, text: str) -> Chunk:
    return Chunk(
        page_content=text,
        metadata=ChunkMetadata(source=source, title="Документация", section="API"),
    )


@pytest.mark.asyncio
async def test_reindex_removes_only_obsolete_chunks(qdrant_store):
    old = await make_chunk("orders.md", "Старая версия")
    obsolete = await make_chunk("orders.md", "Удалённый раздел")
    updated = await make_chunk("orders.md", "Новая версия")
    other_document = await make_chunk("payments.md", "Другой документ")
    await qdrant_store.load_document([old, obsolete], [[1.0, 0.0], [0.0, 1.0]])
    await qdrant_store.load_document([other_document], [[0.0, 1.0]])

    await qdrant_store.load_document([updated], [[1.0, 0.0]])

    chunks = await qdrant_store.search([1.0, 0.0])
    assert len(chunks) == 2
    assert updated in chunks
    assert other_document in chunks


@pytest.mark.asyncio
async def test_repeated_upload_does_not_duplicate_points(qdrant_store):
    chunk = await make_chunk("orders.md", "Документация заказов")
    await qdrant_store.load_document([chunk], [[1.0, 0.0]])

    await qdrant_store.load_document([chunk], [[1.0, 0.0]])

    result = await qdrant_store.client.count(
        collection_name=qdrant_store.collection,
        exact=True,
    )
    assert result.count == 1
