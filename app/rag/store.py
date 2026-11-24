from uuid import uuid5, NAMESPACE_URL

from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.rag.schemas import Chunk


class QdrantStore:
    def __init__(self, client: AsyncQdrantClient, collection: str):
        self.client = client
        self.collection = collection

    async def _ensure_collection(self, vector_size: int) -> None:
        if await self.client.collection_exists(self.collection):
            return

        try:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
        except UnexpectedResponse as exc:
            if not await self.client.collection_exists(self.collection):
                raise

    async def search(self, vector: list[float]) -> list[Chunk]:
        response = await self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=3,
            with_payload=True,
        )

        chunks: list[Chunk] = []
        for point in response.points:
            if point.payload is None:
                continue

            chunks.append(Chunk.model_validate(point.payload))

        return chunks

    async def load_document(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        points = [
            models.PointStruct(
                id=str(uuid5(NAMESPACE_URL, f"{chunk.metadata.source}:{position}")),
                vector=vector,
                payload=chunk.model_dump()
            )
            for position, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ]

        if not points:
            return

        path = chunks[0].metadata.source

        await self._ensure_collection(len(vectors[0]))

        await self.client.upsert(
            collection_name=self.collection,
            points=points,
            wait=True,
        )

        await self.client.delete(
            self.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(key="metadata.source", match=models.MatchValue(value=path))
                    ],
                    must_not=[models.HasIdCondition(has_id=[point.id for point in points])],
                )
            ),
            wait=True,
        )
