from pydantic import BaseModel

class PageResponse(BaseModel):
    page: int
    text: str