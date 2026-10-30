from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime

    class Config:
        from_attributes = True