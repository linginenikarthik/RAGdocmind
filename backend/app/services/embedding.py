
# # app/services/embedding.py

# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")


# def generate_embedding(text: str):
#     embedding = model.encode(
#         text, 
#         convert_to_numpy=True
#     )
#     return embedding.tolist()

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    token_count = len(
        model.tokenizer(
            text,
            add_special_tokens=True,
            truncation=False,
        )["input_ids"]
    )

    if token_count > model.max_seq_length:
        raise ValueError(
            f"Text has {token_count} tokens; "
            f"model limit is {model.max_seq_length}."
        )

    vector = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )

    return vector.astype("float32").tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    for text in texts:
        token_count = len(
            model.tokenizer(
                text,
                add_special_tokens=True,
                truncation=False,
            )["input_ids"]
        )

        if token_count > model.max_seq_length:
            raise ValueError(
                f"Chunk exceeds model token limit: {token_count}"
            )

    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=False,
        batch_size=32,
        show_progress_bar=False,
    )

    return vectors.astype("float32").tolist()