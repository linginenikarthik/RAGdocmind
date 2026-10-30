# from sqlalchemy.orm import Session

# from models.chunk import Chunk

# from services.pdf_loader import extract_text_from_pdf
# from services.chunker import chunk_pages
# from services.embedding import generate_embedding
# from services.vector_store import load_index, add_vectors


# def ingest_document(document, db: Session):
#     """
#     Complete RAG ingestion pipeline

#     PDF
#       ↓
#     Extract text
#       ↓
#     Chunk
#       ↓
#     MiniLM Embedding
#       ↓
#     Store in FAISS
#       ↓
#     Store metadata in SQLite
#     """

#     # 1. Extract page-wise text
#     pages = extract_text_from_pdf(document.file_path)

#     # 2. Create chunks
#     chunks = chunk_pages(pages)

#     # 3. Generate embeddings
#     vectors = []
#     for chunk in chunks:
#         vector = generate_embedding(chunk["text"])
#         vectors.append(vector)

#     # Current FAISS size (starting position)
#     current_index = load_index().ntotal

#     # 4. Store vectors in FAISS
#     total_vectors = add_vectors(vectors)

#     # 5. Store chunk metadata in SQLite
#     for i, chunk in enumerate(chunks):

#         db_chunk = Chunk(
#             faiss_index=current_index + i,
#             document_id=document.id,
#             page=chunk["page"],
#             chunk_index=chunk["chunk_index"],
#             text=chunk["text"]
#         )

#         db.add(db_chunk)

#     db.commit()

#     return {
#         "document_id": document.id,
#         "chunks_created": len(chunks),
#         "vectors_in_faiss": total_vectors
#     }

from sqlalchemy.orm import Session

from models.chunk import Chunk
from services.chunking import chunk_pdf
from services.embedding import generate_embeddings
from services.vector_store import add_vectors, load_index


def ingest_document(document, db: Session):
    # 1. Parse and chunk the PDF.
    chunks = chunk_pdf(document.file_path)

    if not chunks:
        return {
            "document_id": document.id,
            "chunks_created": 0,
            "vectors_in_faiss": load_index().ntotal,
        }

    # 2. Generate one embedding per chunk.
    texts = [chunk["text"] for chunk in chunks]
    vectors = generate_embeddings(texts)

    # 3. Add embeddings and get their actual FAISS row IDs.
    faiss_ids = add_vectors(vectors)

    if len(faiss_ids) != len(chunks):
        raise RuntimeError("FAISS ID count does not match chunk count.")

    # 4. Save chunk text and matching FAISS IDs in SQL.
    db_chunks = [
        Chunk(
            faiss_index=faiss_id,
            document_id=document.id,
            page=chunk["page"],
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
        )
        for chunk, faiss_id in zip(chunks, faiss_ids)
    ]

    try:
        db.add_all(db_chunks)
        db.commit()
    except Exception:
        db.rollback()
        # FAISS has already changed. Rebuild/reconcile before
        # accepting another ingestion operation.
        raise

    return {
        "document_id": document.id,
        "chunks_created": len(chunks),
        "vectors_in_faiss": load_index().ntotal,
    }