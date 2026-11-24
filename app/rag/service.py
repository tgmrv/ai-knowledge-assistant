from app.rag.markdown import split_markdown
from app.rag.models import ModelsService
from app.rag.schemas import Chunk
from app.rag.store import QdrantStore


class RAGService:
    def __init__(self, vector_store: QdrantStore, models: ModelsService) -> None:
        self.store = vector_store
        self.models = models

    async def index(self, text: str, source: str) -> None:
        chunks = split_markdown(text, source)

        texts = [chunk.page_content for chunk in chunks]

        vectors = await self.models.embed_documents(texts)
        await self.store.load_document(chunks, vectors)

    async def search(self, question: str) -> list[Chunk]:
        vector = await self.models.embed_query(question)
        return await self.store.search(vector)

    async def answer(self, question: str) -> str:
        chunks = await self.search(question)
        return await self.models.generate_answer(question, chunks)
