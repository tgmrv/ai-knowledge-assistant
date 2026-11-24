from collections.abc import AsyncIterator, Iterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from aiogram import Bot
from fastapi.testclient import TestClient
from qdrant_client import AsyncQdrantClient, models

from app.api import main as api_main
from app.rag.service import RAGService
from app.rag.store import QdrantStore


@pytest.fixture
def rag_mock() -> Mock:
    return Mock(spec=RAGService)


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch, rag_mock: Mock) -> Iterator[TestClient]:
    services = SimpleNamespace(rag=rag_mock, close=AsyncMock())
    monkeypatch.setattr(api_main, "Settings", lambda: None)
    monkeypatch.setattr(api_main, "build_services", lambda _: services)

    with TestClient(api_main.app) as client:
        yield client


@pytest.fixture
def telegram_bot_mock() -> Mock:
    return Mock(spec=Bot)


@pytest_asyncio.fixture
async def qdrant_store() -> AsyncIterator[QdrantStore]:
    client = AsyncQdrantClient(":memory:")
    collection = "test_docs"
    try:
        await client.create_collection(
            collection_name=collection,
            vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE),
        )
        yield QdrantStore(client, collection)
    finally:
        await client.close()
