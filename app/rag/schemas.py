from pydantic import BaseModel


class ChunkMetadata(BaseModel):
    source: str
    title: str
    section: str


class Chunk(BaseModel):
    page_content: str
    metadata: ChunkMetadata