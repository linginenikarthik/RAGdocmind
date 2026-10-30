# from sqlalchemy.orm import Session

# from models.chunk import Chunk

# from services.embedding import generate_embedding
# from services.vector_store import search_vectors


# def retrieve(question: str, db: Session, k=3):

#     query_vector = generate_embedding(question)

#     indices, scores = search_vectors(query_vector, k)

#     results = []

#     for idx in indices:

#         chunk = db.query(Chunk).filter(
#             Chunk.faiss_index == int(idx)
#         ).first()

#         if chunk:
#             results.append(chunk)

#     return results


# from sqlalchemy.orm import Session

# from models.chunk import Chunk
# from services.embedding import generate_embedding
# from services.vector_store import search_vectors


# def retrieve(
#     question: str,
#     db: Session,
#     k: int = 8,
# ) -> list[Chunk]:

#     query_vector = generate_embedding(question)

#     indices, distances = search_vectors(
#         query_vector,
#         k=k,
#     )

#     if len(indices) == 0:
#         return []

#     chunks = (
#         db.query(Chunk)
#         .filter(
#             Chunk.faiss_index.in_(
#                 [int(idx) for idx in indices]
#             )
#         )
#         .all()
#     )

#     chunk_by_id = {
#         chunk.faiss_index: chunk
#         for chunk in chunks
#     }

#     # Preserve FAISS ranking: nearest result first.
#     return [
#         chunk_by_id[int(idx)]
#         for idx in indices
#         if int(idx) in chunk_by_id
#     ]




from sqlalchemy.orm import Session

from models.chunk import Chunk
from services.embedding import generate_embedding
from services.vector_store import search_vectors


def retrieve_relevant_chunks(
    query: str,
    db: Session,
    document_id: int | None = None,
    top_k: int = 8,
):
    """
    Retrieve relevant document chunks using FAISS.

    Args:
        query: User's question.
        db: SQLAlchemy database session.
        document_id: Optional document ID to restrict retrieval.
        top_k: Number of FAISS results to request.

    Returns:
        A list of dictionaries containing the retrieved chunk text
        and its metadata, ordered by FAISS similarity.
    """

    if not query or not query.strip():
        return []

    # 1. Generate an embedding for the user's question.
    query_vector = generate_embedding(query.strip())

    # 2. Search FAISS for the closest vectors.
    indices, distances = search_vectors(
        query_vector,
        k=top_k,
    )

    # 3. Remove invalid FAISS indices.
    valid_results = [
        (int(faiss_id), float(distance))
        for faiss_id, distance in zip(indices, distances)
        if int(faiss_id) >= 0
    ]

    if not valid_results:
        print("FAISS returned no valid results.")
        return []

    # 4. Fetch matching database rows in one query.
    faiss_ids = [faiss_id for faiss_id, _ in valid_results]

    rows = (
        db.query(Chunk)
        .filter(Chunk.faiss_index.in_(faiss_ids))
        .all()
    )

    # 5. Build a lookup so database ordering cannot change FAISS ranking.
    chunks_by_faiss_id = {
        int(chunk.faiss_index): chunk
        for chunk in rows
    }

    results = []

    print("\n========== RAG RETRIEVAL DEBUG ==========")
    print(f"Question: {query}")
    print(f"Requested top_k: {top_k}")
    print(f"FAISS matches: {len(valid_results)}")

    # 6. Return chunks in FAISS's original ranking order.
    for rank, (faiss_id, distance) in enumerate(valid_results, start=1):
        chunk = chunks_by_faiss_id.get(faiss_id)

        if chunk is None:
            print(
                f"\nRank {rank}: FAISS ID {faiss_id}"
                " has no matching SQLite chunk."
            )
            continue

        # Optional document filtering.
        if (
            document_id is not None
            and chunk.document_id != document_id
        ):
            continue

        print(f"\nRank: {rank}")
        print(f"FAISS ID: {faiss_id}")
        print(f"L2 distance: {distance:.4f}")
        print(f"Document ID: {chunk.document_id}")
        print(f"Page: {chunk.page}")
        print(f"Chunk index: {chunk.chunk_index}")
        print(f"Text: {chunk.text[:700]}")

        results.append(
            {
                "faiss_index": faiss_id,
                "distance": distance,
                "document_id": chunk.document_id,
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
            }
        )

    print(f"\nChunks returned: {len(results)}")
    print("=========================================\n")

    return results


# Backward-compatible alias if your existing code calls retrieve_chunks().
def retrieve(
    query: str,
    db: Session,
    document_id: int | None = None,
    top_k: int = 8,
):
    return retrieve_relevant_chunks(
        query=query,
        db=db,
        document_id=document_id,
        top_k=top_k,
    )
