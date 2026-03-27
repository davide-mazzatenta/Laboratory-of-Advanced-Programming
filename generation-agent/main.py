"""
Generation Agent Service - FastAPI Implementation
Lightweight text generation service using Gemini for document-based generation
Supports both partial (query-based) and full document generation
"""

from typing import List, Optional, Dict, Any, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import os
from contextlib import asynccontextmanager
import asyncio
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API configuration
GEMINI_API_KEYS = [
    "AIzaSyBEsyakskQ7iZnDfnlDGQYwSB0QQJ5fMhA",
    "AIzaSyAEEjrZnXFKR-uonJWnt46iPYdNLQzSqVI",
    "AIzaSyCDQBZ50InkrXIkHI7C0p_Xzg1wjroTUkQ"
]

# Global variables
gemini_model = None
current_gemini_key_index = 0
service_ready = False

def configure_gemini():
    """Configure Gemini with current API key"""
    global gemini_model, current_gemini_key_index
    try:
        genai.configure(api_key=GEMINI_API_KEYS[current_gemini_key_index])
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info(f"Configured Gemini with key index {current_gemini_key_index}")
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {e}")
        raise

def try_next_gemini_key():
    """Switch to next Gemini API key"""
    global current_gemini_key_index
    current_gemini_key_index = (current_gemini_key_index + 1) % len(GEMINI_API_KEYS)
    configure_gemini()
    logger.info(f"Switched to Gemini key index {current_gemini_key_index}")

def initialize_service():
    """Initialize the generation service"""
    global service_ready
    
    try:
        logger.info("Initializing Generation Agent Service...")
        
        # Configure Gemini
        configure_gemini()
        
        service_ready = True
        logger.info("Generation Agent Service initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {str(e)}")
        service_ready = False
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize service
    logger.info("Starting Generation Agent Service...")
    await asyncio.get_event_loop().run_in_executor(None, initialize_service)
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down Generation Agent Service...")

app = FastAPI(
    title="Generation Agent Service",
    lifespan=lifespan
)

# Document service URL (will be resolved via API Gateway)
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://document-service:8000")

# Pydantic models
class GenerationRequest(BaseModel):
    document_id: str  # Format: userId_projectId_docId
    query: str  # The generation query/instruction
    full_doc: bool = False  # True for full doc generation, False for query-based
    agent_id: str = "generation-agent"
    execution_id: Optional[str] = None

class GenerationResponse(BaseModel):
    success: bool
    agent_id: str
    document_id: str
    execution_id: Optional[str]
    query: str
    full_doc: bool
    generated_content: str
    source_mode: str  # "full_text", "query", "chunked_text"
    chunks_used: int
    message: str

def generate_with_gemini(query: str, text_content: str, full_doc: bool = False) -> str:
    """Generate content with Gemini based on query and text"""
    global gemini_model
    
    if not gemini_model:
        raise HTTPException(status_code=503, detail="Gemini not available")
    
    if not query.strip() or not text_content.strip():
        raise HTTPException(status_code=400, detail="Query and text content are required")
    
    # Create prompt based on generation type
    if full_doc:
        prompt = f"""Basandoti sul contenuto del seguente documento fornisci una risposta a {query}

Documento:
{text_content}

Fornisci una risposta concisa e ben strutturata o rigenera parti o riempi i campi(in questo caso riproduci fedelmente il documento) se necessario"""
    else:
        prompt = f"""Basandoti sul contenuto del seguente documento fornisci una risposta a questo task: {query}

contenuto:
{text_content}

Fornisci una risposta concisa e rilevante."""

    # Try each Gemini API key until one works
    for attempt in range(len(GEMINI_API_KEYS)):
        try:
            logger.info(f"Attempting Gemini generation with key index {current_gemini_key_index}")
            
            response = gemini_model.generate_content(
                prompt, 
                generation_config={"temperature": 0.3, "max_output_tokens": 2048}
            )
            
            if response.text:
                logger.info("Gemini generation successful")
                return response.text
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
            if attempt < len(GEMINI_API_KEYS) - 1:
                try_next_gemini_key()
            else:
                logger.error("All Gemini API keys failed")
                raise HTTPException(status_code=503, detail="Gemini generation failed")
    
    raise HTTPException(status_code=503, detail="Gemini generation failed")

def generate_chunked_content(query: str, chunks: List[str], full_doc: bool = False) -> str:
    """Generate content from multiple chunks by processing them iteratively"""
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")
    
    if len(chunks) == 1:
        return generate_with_gemini(query, chunks[0], full_doc)
    
    # For multiple chunks, we'll generate from each and then synthesize
    chunk_results = []
    
    for i, chunk in enumerate(chunks):
        try:
            chunk_query = f"{query} (Focus on content from section {i+1} of {len(chunks)})"
            result = generate_with_gemini(chunk_query, chunk, False)  # Process chunks individually
            chunk_results.append(result)
        except Exception as e:
            logger.warning(f"Failed to process chunk {i+1}: {e}")
            continue
    
    if not chunk_results:
        raise HTTPException(status_code=500, detail="Failed to process any chunks")
    
    # Synthesize results if multiple chunks were processed
    if len(chunk_results) > 1:
        synthesis_prompt = f"Sintetizza e combina le seguenti risposte parziali in una risposta coerente e completa per: {query}\n\n"
        synthesis_prompt += "\n\n".join([f"Part {i+1}:\n{result}" for i, result in enumerate(chunk_results)])
        
        try:
            final_result = generate_with_gemini("Creare una risposta unificata e ben strutturata", synthesis_prompt, True)
            return final_result
        except Exception as e:
            logger.warning(f"Synthesis failed: {e}, returning combined results")
            return "\n\n".join(chunk_results)
    
    return chunk_results[0]

async def fetch_document_content(document_id: str, query: Optional[str] = None, is_query: bool = False) -> Dict[str, Any]:
    """Fetch document content from document service via API Gateway"""
    try:
        # Parse document_id: userId_projectId_docId
        # Handle cases where project_id might contain underscores or spaces
        parts = document_id.split('_')
        if len(parts) < 3:
            raise ValueError(f"Invalid document_id format: {document_id}. Expected format: userId_projectId_docId")
        
        # Extract user_id (first part), doc_id (last part), and project_id (everything in between)
        user_id = parts[0]
        doc_id = parts[-1]
        project_id = '_'.join(parts[1:-1])  # Join middle parts in case project_id contains underscores
        
        logger.info(f"Parsed document_id: user_id={user_id}, project_id={project_id}, doc_id={doc_id}")
        
        # Call document service via API Gateway
        # URL encode the project_id to handle spaces and special characters
        from urllib.parse import quote
        encoded_project_id = quote(project_id, safe='')
        url = f"{DOCUMENT_SERVICE_URL}/api/v1/documents/{user_id}/{encoded_project_id}/{doc_id}/text"
        
        logger.info(f"Requesting document content from: {url}")
        
        params = {}
        if is_query and query:
            params = {"is_query": True, "query": query}
        
        response = requests.get(url, params=params, timeout=30)
        
        logger.info(f"Document service response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Document service error: {response.text}")
        
        response.raise_for_status()
        
        return response.json()
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail=f"Failed to fetch document content: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Health check endpoint
@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "generation-agent",
        "gemini_configured": gemini_model is not None,
        "service_ready": service_ready
    }

# Main generation endpoint
@app.post("/api/v1/agents/generate", response_model=GenerationResponse)
async def generate_content(request: GenerationRequest):
    """Generate content from document using Gemini"""
    
    if not service_ready:
        raise HTTPException(status_code=503, detail="Generation service not ready")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    if not request.document_id.strip():
        raise HTTPException(status_code=400, detail="Document ID is required")
    
    try:
        # Fetch document content based on generation type
        if request.full_doc:
            # Full document generation - get all content
            logger.info(f"Fetching full document for generation: {request.document_id}")
            doc_data = await fetch_document_content(request.document_id, None, False)
        else:
            # Query-based generation - get relevant chunks, but fallback to full content if empty
            logger.info(f"Fetching relevant content for query: {request.query}")
            doc_data = await fetch_document_content(request.document_id, request.query, True)
            
            # If query-based search returns no chunks, fallback to full document
            if not doc_data.get("chunks") or len(doc_data["chunks"]) == 0:
                logger.info(f"No relevant chunks found for query, falling back to full document")
                doc_data = await fetch_document_content(request.document_id, None, False)
        
        if not doc_data.get("chunks"):
            raise HTTPException(
                status_code=404, 
                detail="No content found in document"
            )
        
        chunks = doc_data["chunks"]
        source_mode = doc_data.get("mode", "unknown")
        chunks_used = len(chunks)
        
        # Extract text content from chunks
        text_chunks = [chunk["text"] for chunk in chunks if chunk.get("text", "").strip()]
        
        if not text_chunks:
            raise HTTPException(status_code=404, detail="No text content found")
        
        # Generate content
        if len(text_chunks) == 1:
            # Single chunk/full text
            generated_content = generate_with_gemini(request.query, text_chunks[0], request.full_doc)
        else:
            # Multiple chunks
            generated_content = generate_chunked_content(request.query, text_chunks, request.full_doc)
        
        return GenerationResponse(
            success=True,
            agent_id=request.agent_id,
            document_id=request.document_id,
            execution_id=request.execution_id,
            query=request.query,
            full_doc=request.full_doc,
            generated_content=generated_content,
            source_mode=source_mode,
            chunks_used=chunks_used,
            message=f"Successfully generated content from {chunks_used} chunk(s) using {source_mode} mode"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Alternative endpoint for orchestrator compatibility
@app.post("/api/v1/agents/process")
async def process_agent_task(request: dict):
    """Process agent task (orchestrator compatibility endpoint)"""
    
    agent_id = request.get("agentId")
    prompt = request.get("prompt", "")
    document_ids = request.get("documentIds", [])
    execution_id = request.get("executionId")
    full_doc = request.get("fullDoc", False)
    
    if agent_id != "generation-agent":
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    if not document_ids:
        raise HTTPException(status_code=400, detail="No document IDs provided")
    
    # Use first document ID (extend later if multiple docs needed)
    document_id = document_ids[0]
    
    generation_request = GenerationRequest(
        document_id=document_id,
        query=prompt,
        full_doc=full_doc,
        agent_id=agent_id,
        execution_id=execution_id
    )
    
    result = await generate_content(generation_request)
    
    return {
        "agentId": agent_id,
        "prompt": prompt,
        "documentIds": document_ids,
        "executionId": execution_id,
        "response": result.generated_content,
        "completedAt": None,  # Could add timestamp if needed
        "fullResult": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)