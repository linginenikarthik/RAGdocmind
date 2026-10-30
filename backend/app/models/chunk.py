from sqlalchemy import Column, Integer, Text, ForeignKey
from database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    faiss_index = Column(Integer, unique=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"))

    page = Column(Integer)

    chunk_index = Column(Integer)

    text = Column(Text)