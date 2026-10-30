from xmlrpc import client

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from pathlib import types
from sqlalchemy.orm import Session
import os
import shutil

from database import get_db
from models.document import Document
from schemas.document import DocumentResponse
from schemas.query import QueryRequest

from services.pdf_loader import extract_text_from_pdf
from schemas.page import PageResponse
from typing import List
from services.chunker import chunk_pages
from schemas.chunk import ChunkResponse
from services.rag_pipeline import ingest_document
from services.rag import rag_answer
import os
from google import genai

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        file_name=file.filename,
        file_path=file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get("/{document_id}/pages", response_model=List[PageResponse])
def get_pdf_pages(document_id: int, db: Session = Depends(get_db)):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    pages = extract_text_from_pdf(document.file_path)

    return pages

@router.get("/{document_id}/chunks",
            response_model=list[ChunkResponse])
def get_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(404, "Document not found")

    pages = extract_text_from_pdf(document.file_path)

    chunks = chunk_pages(pages)

    return chunks

@router.post("/{document_id}/ingest")
def ingest_pdf(document_id: int,
               db: Session = Depends(get_db)):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="D ocument not found"
        )

    result = ingest_document(document, db)

    return result

@router.post("/ask")
def ask_question(
    request: QueryRequest,
    db: Session = Depends(get_db)
):

    return rag_answer(request.question, db)



@router.get("/list_models")
def list_models():
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    for model in client.models.list():
        print("Model:", model.name)
        print("Display name:", model.display_name)
        print("Supported actions:", model.supported_actions)
        print("-" * 50)

@router.get("/test_gemnini_res")
def test_gemini_response():
    import time
    from google.genai import types
    client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=30000
    )
    )

    start = time.perf_counter()

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="What is 10 + 20?",
    )

    print("Answer:", response.text)
    print("Time:", time.perf_counter() - start)