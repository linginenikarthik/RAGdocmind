import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")


def chunk_pages(
    pages: list,
    chunk_size: int = 500,
    overlap: int = 50
):

    chunks = []

    chunk_index = 0

    for page in pages:

        tokens = encoding.encode(page["text"])

        start = 0

        while start < len(tokens):

            end = start + chunk_size

            chunk_tokens = tokens[start:end]

            chunk_text = encoding.decode(chunk_tokens)

            chunks.append({
                "page": page["page"],
                "chunk_index": chunk_index,
                "text": chunk_text
            })

            chunk_index += 1

            start += chunk_size - overlap

    return chunks