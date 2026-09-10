import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import rag_engine

app = FastAPI(title="ApexHaven AI Document RAG Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_docs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory session tracking for dashboard metrics
chat_history_store = []

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

@app.get("/api/stats")
def get_stats():
    stats = rag_engine.get_system_stats()
    return {
        "total_documents": stats["total_documents"],
        "total_chunks": stats["total_chunks"],
        "total_queries": len(chat_history_store),
        "document_list": stats["document_list"]
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = rag_engine.ingest_document(file_path, filename)
    if result.get("status") == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to process document"))

    return result

@app.delete("/api/documents/{doc_name}")
def delete_doc(doc_name: str):
    success = rag_engine.delete_document(doc_name)
    file_path = os.path.join(UPLOAD_DIR, doc_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
    if not success:
        raise HTTPException(status_code=404, detail="Document could not be deleted from vector store")
    return {"message": f"Document '{doc_name}' deleted successfully."}

@app.post("/api/reprocess/{doc_name}")
def reprocess_doc(doc_name: str):
    file_path = os.path.join(UPLOAD_DIR, doc_name)
    if not os.path.exists(file_path):
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_documents", doc_name)
        if os.path.exists(sample_path):
            file_path = sample_path
        else:
            raise HTTPException(status_code=404, detail=f"File {doc_name} not found on disk to re-process.")

    rag_engine.delete_document(doc_name)
    result = rag_engine.ingest_document(file_path, doc_name)
    return result

@app.post("/api/chat", response_model=QueryResponse)
def chat_endpoint(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = rag_engine.query_rag(req.query)
    chat_history_store.append({
        "query": req.query,
        "answer": result["answer"],
        "sources": result["sources"]
    })
    return result

@app.get("/api/history")
def get_history():
    return chat_history_store

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()