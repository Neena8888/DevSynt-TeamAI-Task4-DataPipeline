import os
import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv
import pypdf
import docx
import chromadb
from chromadb.utils import embedding_functions
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables!")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Persistent ChromaDB
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
chroma_client = chromadb.PersistentClient(path=DB_DIR)

# Default embedding function inside Chroma (local & fast)
emb_fn = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(
    name="apex_real_estate_knowledge",
    embedding_function=emb_fn
)

def extract_text_with_metadata(file_path: str, doc_name: str) -> List[Dict[str, Any]]:
    """Extracts text per page/section with metadata based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    pages_data = []

    if ext == ".pdf":
        reader = pypdf.PdfReader(file_path)
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_data.append({"text": text.strip(), "page": idx + 1})

    elif ext == ".docx":
        doc = docx.Document(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        if full_text:
            pages_data.append({"text": full_text, "page": 1})

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
        if full_text.strip():
            pages_data.append({"text": full_text.strip(), "page": 1})

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return pages_data

def chunk_text(pages_data: List[Dict[str, Any]], doc_id: str, doc_name: str, chunk_size: int = 500, overlap: int = 80) -> List[Dict[str, Any]]:
    """Splits extracted text into overlapping chunks while retaining exact page metadata."""
    chunks = []
    chunk_counter = 1

    for page in pages_data:
        text = page["text"]
        page_num = page["page"]
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_content = text[start:end]

            chunk_obj = {
                "id": f"{doc_id}_chunk_{chunk_counter}",
                "text": chunk_content,
                "metadata": {
                    "doc_id": doc_id,
                    "doc_name": doc_name,
                    "page": page_num,
                    "chunk_id": f"{doc_id}_chunk_{chunk_counter}"
                }
            }
            chunks.append(chunk_obj)
            chunk_counter += 1

            if end == len(text):
                break
            start += (chunk_size - overlap)

    return chunks

def ingest_document(file_path: str, doc_name: str) -> Dict[str, Any]:
    """Extracts, chunks, and persists document into vector database."""
    doc_id = str(uuid.uuid4())[:8]
    pages_data = extract_text_with_metadata(file_path, doc_name)
    chunks = chunk_text(pages_data, doc_id, doc_name)

    if not chunks:
        return {"status": "failed", "error": "No text extracted"}

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    return {
        "status": "processed",
        "doc_id": doc_id,
        "doc_name": doc_name,
        "total_pages": len(pages_data),
        "total_chunks": len(chunks)
    }

def delete_document(doc_name: str) -> bool:
    """Removes all chunks associated with a document."""
    try:
        collection.delete(where={"doc_name": doc_name})
        return True
    except Exception:
        return False

def query_rag(user_query: str, top_k: int = 12) -> Dict[str, Any]:
    """Retrieves context chunks and generates grounded answers via Gemini Flash."""
    # Retrieve top relevant chunks (or all available if collection is compact)
    results = collection.query(
        query_texts=[user_query],
        n_results=top_k
    )

    retrieved_docs = results["documents"][0] if results["documents"] else []
    retrieved_metas = results["metadatas"][0] if results["metadatas"] else []

    if not retrieved_docs:
        return {
            "answer": "The information could not be found in the uploaded documents.",
            "sources": []
        }

    # Deduplicate sources while retaining document context
    context_blocks = []
    sources = []
    for doc_text, meta in zip(retrieved_docs, retrieved_metas):
        source_label = f"{meta['doc_name']} — Page {meta['page']}"
        context_blocks.append(f"[{source_label}]\n{doc_text}")
        if source_label not in sources:
            sources.append(source_label)

    context_str = "\n\n".join(context_blocks)

    prompt = f"""You are the official AI Assistant for ApexHaven Properties.
Answer the user's question accurately using ONLY the provided document context below.

INSTRUCTIONS:
1. Synthesize information across multiple documents/pages if the question asks about multiple topics.
2. If the context contains sufficient information to answer the question (or parts of it), provide the grounded factual answer.
3. CRITICAL GUARDRAIL: If the requested information is completely absent from the context, respond strictly with:
   "The information could not be found in the uploaded documents."
4. Never assume, extrapolate, or rely on outside knowledge.

DOCUMENT CONTEXT:
{context_str}

USER QUESTION:
{user_query}

GROUNDED ANSWER:"""

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        answer_text = response.text.strip()
    except Exception as e:
        answer_text = f"Error generating answer from AI: {str(e)}"

    if "The information could not be found in the uploaded documents" in answer_text:
        sources = []

    return {
        "answer": answer_text,
        "sources": sources
    }

def get_system_stats() -> Dict[str, Any]:
    """Aggregates metrics for the frontend dashboard."""
    all_data = collection.get()
    unique_docs = set()
    for meta in all_data["metadatas"]:
        unique_docs.add(meta["doc_name"])

    return {
        "total_documents": len(unique_docs),
        "total_chunks": len(all_data["ids"]),
        "document_list": list(unique_docs)
    }

if __name__ == "__main__":
    print("Testing RAG Engine setup...")
    print("Stats:", get_system_stats())