"""
Document Storage Service - FastAPI Implementation
Handles PDF document storage, retrieval, and text extraction
Now integrated with Chunker Service for automatic chunking
"""

from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn
import requests
import tempfile
import os
import uuid

from database import DatabaseManager
from pdf_processor import PDFProcessor

# URL del chunker service (in Docker sarà il nome del servizio)
CHUNKER_URL = os.getenv("CHUNKER_URL", "http://chunker-service:8000")
CHUNK_LIMIT_CHARS = 4000  # Define the limit for chunking

app = FastAPI(title="Document Storage Service")

# Initialize services
db_manager = DatabaseManager()
pdf_processor = PDFProcessor()


# Pydantic models
class DocumentResponse(BaseModel):
    success: bool
    message: str
    doc_id: str
    chunks: List[dict] = []


class DocumentMetadata(BaseModel):
    doc_id: str
    title: str
    content: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]


class ProjectInfo(BaseModel):
    project_id: str
    document_count: int


class ProjectListResponse(BaseModel):
    projects: List[ProjectInfo]


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "document-service"}


# Get user projects
@app.get("/api/v1/projects/{user_id}", response_model=ProjectListResponse)
async def get_user_projects(user_id: str):
    """Get all projects for a user"""
    try:
        projects = db_manager.list_user_projects(user_id)
        return ProjectListResponse(projects=projects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")


# Document upload endpoint
@app.post("/api/v1/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    project_id: str = Form(...),
    title: str = Form(...),
    doc_id: Optional[str] = Form(None)
):
    """Upload a document to a project and store its chunks+embeddings"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if not doc_id:
        doc_id = str(uuid.uuid4())

    file_content = await file.read()
    text_content = pdf_processor.extract_text_from_bytes(file_content)
    document_id = f"{user_id}_{project_id}_{doc_id}"

    # Store document binary + text
    success = db_manager.store_document(
        document_id, user_id, project_id, doc_id, title, file_content, text_content
    )

    temp_path = None
    chunks_data = []
    try:
        # Create temporary file for chunker service
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_content)
            temp_path = tmp.name

        print(f"📄 Sending document to chunker service: {file.filename}")
        print(f"📊 File size: {len(file_content)} bytes")
        
        # Call chunker service with increased timeout
        with open(temp_path, "rb") as f:
            files = {"file": (file.filename, f)}
            print(f"🔗 Calling chunker at: {CHUNKER_URL}/chunk")
            r = requests.post(f"{CHUNKER_URL}/chunk", files=files, timeout=300)  # 5 minute timeout

        print(f"📋 Chunker response status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"❌ Chunker error response: {r.text}")
            raise HTTPException(status_code=500, detail=f"Chunker error: {r.text}")

        chunks_from_service = r.json().get("chunks", [])
        print(f"✅ Received {len(chunks_from_service)} chunks from chunker service")

        chunks_to_store = [{
            "id": f"{document_id}_{i}",
            "user_id": user_id,
            "project_id": project_id,
            "doc_id": doc_id,
            "chunk_index": i,
            "chunk_text": chunk['text'],
            "embedding": chunk['embedding']
        } for i, chunk in enumerate(chunks_from_service)]

        print(f"💾 Storing {len(chunks_to_store)} chunks in database...")
        if not db_manager.store_chunks(chunks_to_store):
            raise HTTPException(status_code=500, detail="Failed to store chunks in database.")

        # Remove embeddings from response (they're large)
        for chunk in chunks_to_store:
            chunk.pop("embedding", None)

        chunks_data = chunks_to_store

    except Exception as e:
        print(f"Error during chunking or storage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    if success:
        return DocumentResponse(
            success=True,
            message="Document uploaded and chunked successfully",
            doc_id=doc_id,
            chunks=chunks_data
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store document")


# Document retrieval endpoint (PDF binary)
@app.get("/api/v1/documents/{user_id}/{project_id}/{doc_id}")
async def get_document(user_id: str, project_id: str, doc_id: str):
    """Get document PDF binary"""
    document_id = f"{user_id}_{project_id}_{doc_id}"
    document_data = db_manager.get_document(document_id)

    if not document_data:
        raise HTTPException(status_code=404, detail="Document not found")

    return Response(content=document_data, media_type="application/pdf")


# Alternative endpoint with /pdf suffix
@app.get("/api/v1/documents/{user_id}/{project_id}/{doc_id}/pdf")
async def get_document_pdf(user_id: str, project_id: str, doc_id: str):
    """Get document PDF binary (alternative endpoint with /pdf suffix)"""
    return await get_document(user_id, project_id, doc_id)


@app.get("/api/v1/documents/{user_id}/{project_id}/{doc_id}/text")
async def get_document_text(
    user_id: str,
    project_id: str,
    doc_id: str,
    is_query: bool = Query(False, description="Set true if this is a query request"),
    query: Optional[str] = Query(None, description="Query text if is_query=true"),
    full_chunks: bool = Query(False, description="Return all chunks even for large documents")
):
    """
    Restituisce il testo del documento oppure, se il documento è grande e viene fornita una query,
    i chunk più rilevanti. Se full_chunks=true, restituisce sempre tutti i chunk.
    """
    document_id = f"{user_id}_{project_id}_{doc_id}"
    text_content = db_manager.get_document_text(document_id)

    if text_content is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check document size first, regardless of the 'is_query' flag.
    # If the document is small, always return the full text.
    if len(text_content) <= CHUNK_LIMIT_CHARS and not full_chunks:
        return {
            "success": True,
            "mode": "full_text",
            "message": "Document is within the character limit, returning full text.",
            "chunks": [{"text": text_content}]
        }

    # If full_chunks is requested, get all chunks from database
    if full_chunks:
        try:
            all_chunks = db_manager.get_all_chunks(user_id, project_id, doc_id)
            if all_chunks:
                return {
                    "success": True,
                    "mode": "all_chunks", 
                    "message": f"Returning all {len(all_chunks)} chunks for full document processing.",
                    "chunks": all_chunks
                }
            else:
                # Fallback to chunking the full text if no chunks in DB
                chunks = [{"text": text_content[i:i+CHUNK_LIMIT_CHARS]}
                         for i in range(0, len(text_content), CHUNK_LIMIT_CHARS)]
                return {
                    "success": True,
                    "mode": "chunked_text",
                    "message": "No chunks in database, returning text split into chunks.",
                    "chunks": chunks
                }
        except Exception as e:
            # Fallback to text chunking if database chunks fail
            chunks = [{"text": text_content[i:i+CHUNK_LIMIT_CHARS]}
                     for i in range(0, len(text_content), CHUNK_LIMIT_CHARS)]
            return {
                "success": True,
                "mode": "chunked_text",
                "message": "Database chunks unavailable, returning text split into chunks.",
                "chunks": chunks
            }

    # If the document is large, check for a query.
    if is_query and query:
        try:
            r = requests.post(f"{CHUNKER_URL}/embed-query", json={"query": query}, timeout=30)
            if r.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Embedding error: {r.text}")
            query_embedding = r.json().get("embedding")
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error contacting chunker service: {str(e)}")

        best_chunks = db_manager.get_best_chunks(
            user_id, project_id, doc_id, query_embedding, limit=7
        )

        return {
            "success": True,
            "mode": "query",
            "message": "Returning relevant chunks based on query.",
            "chunks": best_chunks
        }
    
    # Fallback if no query is provided for a large document
    if not is_query:
        return {
            "success": True,
            "mode": "chunked_text",
            "message": "Document exceeds character limit, returning raw chunks.",
            "chunks": [{"text": text_content[i:i+CHUNK_LIMIT_CHARS]}
                       for i in range(0, len(text_content), CHUNK_LIMIT_CHARS)]
        }

    # This handles the edge case where is_query is true but no query text is provided
    raise HTTPException(status_code=400, detail="Query flag is true but no query text provided")



# List project documents
@app.get("/api/v1/documents/{user_id}/{project_id}", response_model=DocumentListResponse)
async def list_project_documents(user_id: str, project_id: str):
    """Get all documents in a project"""
    documents = db_manager.list_project_documents(user_id, project_id)
    return DocumentListResponse(documents=documents)


#  new endpoint for getting all chunks
@app.get("/api/v1/documents/{user_id}/{project_id}/{doc_id}/chunks")
async def get_document_chunks(
    user_id: str,
    project_id: str,
    doc_id: str,
    limit: Optional[int] = Query(None, description="Limit number of chunks returned")
):
    """
    Get all chunks for a document (useful for full document generation)
    """
    try:
        chunks = db_manager.get_all_chunks(user_id, project_id, doc_id, limit)
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No chunks found for document")
        
        return {
            "success": True,
            "mode": "all_chunks",
            "message": f"Retrieved {len(chunks)} chunks for document",
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document chunks: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
