# from services.retriever import retrieve
# from services.llm import ask_llm
# from services.retriever import retrieve_relevant_chunks


# def rag_answer(question, db):

#     chunks = retrieve_relevant_chunks(
#         query=question,
#         db=db,
#         top_k=8,
#     )

#     context = ""
#     pages=[]

#     for chunk in chunks:
#         context += chunk["text"] + "\n\n"

#         pages.append(chunk.page)

#     # answer = ask_llm(question, context)
#     answer = context
#     print("RAG answer:", answer)

#     return {
#         "answer": answer,
#         "pages": sorted(set(pages))
#     }


from services.retriever import retrieve_relevant_chunks
from services.llm import ask_llm
import time


def rag_answer(question, db):

    chunks = retrieve_relevant_chunks(
        query=question,
        db=db,
        top_k=8,
    )

    if not chunks:
        return {
            "answer": "I could not find relevant information in the document.",
            "pages": [],
        }

    # Build context from retrieved chunks.
    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
        if chunk.get("text")
    )

    # Collect page numbers from retrieved chunks.
    pages = [
        chunk["page"]
        for chunk in chunks
        if chunk.get("page") is not None
    ]
    start_time = time.time()
    print("Started connection to gemini api",start_time)
    # Generate the answer using your LLM.
    answer = ask_llm(question, context)
    print("Time taken to get answer from gemini api",time.time()-start_time)
    # answer = context

    print("RAG answer:", answer)

    return {
        "answer": answer,
        "pages": sorted(set(pages)),
    }
