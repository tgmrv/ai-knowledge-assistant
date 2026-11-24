from dataclasses import dataclass

from qdrant_client import AsyncQdrantClient

from app.core.config import Settings
from app.rag.models import ModelsService
from app.rag.service import RAGService
from app.rag.store import QdrantStore


@dataclass
class Services:
    rag: RAGService
    qdrant: AsyncQdrantClient

    async def close(self) -> None:
        await self.qdrant.close()

def build_services(settings: Settings) -> Services:
    qdrant = AsyncQdrantClient(
        url=settings.QDRANT_URL,
        check_compatibility=False,
    )
    store = QdrantStore(client=qdrant, collection=settings.COLLECTION)
    models = ModelsService(
        settings.OLLAMA_URL,
        settings.EMBEDDING_MODEL_NAME,
        settings.CHAT_MODEL_NAME,
    )
    rag = RAGService(store, models)
    return Services(
        rag=rag,
        qdrant=qdrant,
    )