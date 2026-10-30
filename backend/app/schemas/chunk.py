from pydantic import BaseModel

class ChunkResponse(BaseModel):
    page: int
    chunk_index: int
    text: str