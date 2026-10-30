from pathlib import Path

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from services.embedding import model


MAX_CHUNK_TOKENS = 200


def _split_oversized_text(text: str) -> list[str]:
    """Split a chunk using MiniLM's own tokenizer when necessary."""

    tokenizer = model.tokenizer
    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
    )

    pieces = []

    for start in range(0, len(token_ids), MAX_CHUNK_TOKENS):
        piece_ids = token_ids[start:start + MAX_CHUNK_TOKENS]
        piece = tokenizer.decode(
            piece_ids,
            skip_special_tokens=True,
        ).strip()

        if piece:
            pieces.append(piece)

    return pieces


def chunk_pdf(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    elements = partition_pdf(
        filename=str(path),
        strategy="fast",
    )

    chunks = chunk_by_title(
        elements,
        max_characters=700,
        new_after_n_chars=550,
        combine_text_under_n_chars=150,
        multipage_sections=False,
    )

    results = []

    for chunk in chunks:
        text = str(chunk).strip()

        if not text:
            continue

        metadata = getattr(chunk, "metadata", None)
        page = getattr(metadata, "page_number", None)

        if page is None:
            original_elements = (
                getattr(metadata, "orig_elements", None) or []
            )

            for element in original_elements:
                element_metadata = getattr(
                    element, "metadata", None
                )
                page = getattr(
                    element_metadata, "page_number", None
                )

                if page is not None:
                    break

        token_ids = model.tokenizer(
            text,
            add_special_tokens=True,
            truncation=False,
        )["input_ids"]

        if len(token_ids) > model.max_seq_length:
            safe_pieces = _split_oversized_text(text)
        else:
            safe_pieces = [text]

        for piece in safe_pieces:
            results.append({
                "page": page,
                "chunk_index": len(results),
                "text": piece,
            })

    return results