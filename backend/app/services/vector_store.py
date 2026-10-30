# import faiss
# import numpy as np
# import os
# import faiss
# import numpy as np
# # MiniLM embedding dimension
# DIMENSION = 384

# INDEX_DIR = "faiss_index"
# INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")

# os.makedirs(INDEX_DIR, exist_ok=True)


# def load_index():
#     if os.path.exists(INDEX_PATH):
#         return faiss.read_index(INDEX_PATH)

#     return faiss.IndexFlatL2(DIMENSION)


# def save_index(index):
#     faiss.write_index(index, INDEX_PATH)


# def add_vectors(vectors):
#     index = load_index()

#     array = np.array(vectors, dtype="float32")

#     index.add(array)

#     save_index(index)

#     return index.ntotal



# def search_vectors(query_vector, k=3):

#     index = load_index()

#     query = np.array(
#         [query_vector],
#         dtype="float32"
#     )

#     distances, indices = index.search(query, k)

#     return indices[0], distances[0]


import os

import faiss
import numpy as np


DIMENSION = 384

INDEX_DIR = "faiss_index"
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")

os.makedirs(INDEX_DIR, exist_ok=True)


def load_index():
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)

        if index.d != DIMENSION:
            raise ValueError(
                f"Expected dimension {DIMENSION}; got {index.d}"
            )

        if not isinstance(index, faiss.IndexFlatL2):
            raise ValueError("Unexpected FAISS index type.")

        return index

    return faiss.IndexFlatL2(DIMENSION)


def save_index(index):
    os.makedirs(INDEX_DIR, exist_ok=True)

    temp_path = INDEX_PATH + ".tmp"
    faiss.write_index(index, temp_path)
    os.replace(temp_path, INDEX_PATH)


def add_vectors(vectors: list) -> list[int]:
    if not vectors:
        return []

    array = np.asarray(vectors, dtype=np.float32)

    if array.ndim != 2 or array.shape[1] != DIMENSION:
        raise ValueError(
            f"Expected shape (n, {DIMENSION}); got {array.shape}"
        )

    if not np.isfinite(array).all():
        raise ValueError("Vectors contain invalid values.")

    index = load_index()
    start_id = index.ntotal

    index.add(array)
    save_index(index)

    return list(range(start_id, index.ntotal))


def search_vectors(query_vector, k: int = 3):
    index = load_index()

    if index.ntotal == 0 or k <= 0:
        return (
            np.asarray([], dtype=np.int64),
            np.asarray([], dtype=np.float32),
        )

    query = np.asarray(
        query_vector,
        dtype=np.float32,
    ).reshape(1, -1)

    if query.shape[1] != DIMENSION:
        raise ValueError(
            f"Expected query dimension {DIMENSION}; "
            f"got {query.shape[1]}"
        )

    if not np.isfinite(query).all():
        raise ValueError("Query vector contains invalid values.")

    distances, indices = index.search(
        query,
        min(k, index.ntotal),
    )

    valid = indices[0] >= 0

    return indices[0][valid], distances[0][valid]