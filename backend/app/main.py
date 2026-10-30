import uvicorn
import sys
sys.path.append("/")  # Add the 'app' directory to the Python path
from fastapi import FastAPI
from database import Base, engine
from api.upload import router as upload_router  
from services.rag_pipeline import ingest_document
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocuMind AI")

app.include_router(upload_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "RAG Backend Running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)