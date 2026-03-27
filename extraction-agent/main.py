"""
Extraction Agent Service - FastAPI Implementation
Lightweight NER extraction service using Italian_NER_XXL model + Gemini post-processing
Optimized for CPU usage and reduced memory footprint
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import os
from contextlib import asynccontextmanager
import asyncio
import logging
import torch
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set PyTorch to use single thread for CPU inference (lighter)
torch.set_num_threads(1)

# Gemini API configuration
GEMINI_API_KEYS = [
    "AIzaSyBEsyakskQ7iZnDfnlDGQYwSB0QQJ5fMhA",
    "AIzaSyAEEjrZnXFKR-uonJWnt46iPYdNLQzSqVI",
    "AIzaSyCDQBZ50InkrXIkHI7C0p_Xzg1wjroTUkQ"
]

# Global variables for model components
nlp_pipeline = None
model_loaded = False
gemini_model = None
current_gemini_key_index = 0

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

def load_ner_model():
    """Load the NER model and tokenizer at startup to avoid cold starts"""
    global nlp_pipeline, model_loaded
    
    try:
        logger.info("Loading Italian NER model (CPU-optimized)...")
        from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
        
        # Load model and tokenizer with CPU optimization
        tokenizer = AutoTokenizer.from_pretrained(
            "DeepMount00/Italian_NER_XXL",
            use_fast=True  # Use fast tokenizer for better performance
        )
        model = AutoModelForTokenClassification.from_pretrained(
            "DeepMount00/Italian_NER_XXL", 
            ignore_mismatched_sizes=True,
            torch_dtype=torch.float32,  # Use float32 for CPU
            low_cpu_mem_usage=True  # Enable memory optimization
        )
        
        # Create NER pipeline with CPU optimizations
        nlp_pipeline = pipeline(
            "ner", 
            model=model, 
            tokenizer=tokenizer, 
            aggregation_strategy="simple",
            device=-1,  # Force CPU usage
            batch_size=1  # Small batch size for memory efficiency
        )
        
        model_loaded = True
        logger.info("NER model loaded successfully on CPU!")
        
        # Configure Gemini
        configure_gemini()
        
    except Exception as e:
        logger.error(f"Failed to load NER model: {str(e)}")
        model_loaded = False
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    logger.info("Starting Extraction Agent Service...")
    await asyncio.get_event_loop().run_in_executor(None, load_ner_model)
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down Extraction Agent Service...")

app = FastAPI(
    title="Extraction Agent Service",
    lifespan=lifespan
)

# Document service URL (will be resolved via API Gateway)
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://document-service:8000")

# Pydantic models
class ExtractionRequest(BaseModel):
    document_ids: List[str]  # Format: userId_projectId_docId
    agent_id: str = "extractor-agent"
    execution_id: Optional[str] = None
    query: Optional[str] = None  # NEW: Query for Gemini post-processing

class EntityResult(BaseModel):
    label: str
    entities: List[str]

class ExtractionResponse(BaseModel):
    success: bool
    agent_id: str
    document_ids: List[str]
    execution_id: Optional[str]
    extracted_entities: str  # Raw concatenated string format
    entities_by_label: List[EntityResult]
    structured_summary: Optional[str] = None  # NEW: Gemini-processed summary
    message: str

def extract_entities_from_text(text: str) -> tuple[str, List[EntityResult]]:
    """Extract entities from text using the loaded NER model"""
    global nlp_pipeline, model_loaded
    
    if not model_loaded or nlp_pipeline is None:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    try:
        # Truncate text if too long to avoid memory issues
        max_length = 5000  # Reasonable limit for processing
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters")
        
        # Run NER with CPU optimization
        with torch.inference_mode():  # Disable gradient computation
            ner_results = nlp_pipeline(text)
        
        # Extract and group entities
        entities_by_label = {}
        for ent in ner_results:
            label = ent["entity_group"]
            entity_text = ent["word"].strip()
            if label not in entities_by_label:
                entities_by_label[label] = []
            if entity_text and entity_text not in entities_by_label[label]:  # avoid duplicates and empty strings
                entities_by_label[label].append(entity_text)
        
        # Create response format
        entity_results = []
        concatenated_entities = []
        
        for label, entities in entities_by_label.items():
            entity_results.append(EntityResult(label=label, entities=entities))
            for entity in entities:
                concatenated_entities.append(f"{label}:{entity}")
        
        concatenated_string = ", ".join(concatenated_entities)
        
        return concatenated_string, entity_results
        
    except Exception as e:
        logger.error(f"Error during NER extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"NER extraction failed: {str(e)}")

def summarize_with_gemini(query: str, extracted_entities: str) -> str:
    """Summarize extracted entities with Gemini based on query"""
    global gemini_model
    
    if not gemini_model:
        logger.warning("Gemini not available, returning raw entities")
        return extracted_entities
    
    if not query or not extracted_entities.strip():
        return extracted_entities
    
    prompt = f"""Sulla base della query seguente e delle entità estratte, riepiloga le entità in un elenco strutturato che risponda direttamente alla query. Includi solo le entità pertinenti alla query.

Query: {query}

Entita estratte: {extracted_entities}

Si prega di fornire un riepilogo strutturato, concentrandosi solo sulle entità che contribuiscono a rispondere alla domanda. Formattare il tutto come un elenco chiaro e organizzato."""

    # Try each Gemini API key until one works
    for attempt in range(len(GEMINI_API_KEYS)):
        try:
            logger.info(f"Attempting Gemini summarization with key index {current_gemini_key_index}")
            
            response = gemini_model.generate_content(
                prompt, 
                generation_config={"temperature": 0.1}
            )
            
            if response.text:
                logger.info("Gemini summarization successful")
                return response.text
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
            if attempt < len(GEMINI_API_KEYS) - 1:
                try_next_gemini_key()
            else:
                logger.error("All Gemini API keys failed")
                return extracted_entities
    
    return extracted_entities

async def fetch_document_text(document_id: str) -> str:
    """Fetch document text from document service via API Gateway"""
    try:
        # Parse document_id: userId_projectId_docId
        parts = document_id.split('_')
        if len(parts) != 3:
            raise ValueError(f"Invalid document_id format: {document_id}")
        
        user_id, project_id, doc_id = parts
        
        # Call document service via API Gateway
        url = f"{DOCUMENT_SERVICE_URL}/api/v1/documents/{user_id}/{project_id}/{doc_id}/text"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("text_content", "")
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail=f"Failed to fetch document text: {str(e)}"
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
        "service": "extraction-agent",
        "model_loaded": model_loaded,
        "gemini_configured": gemini_model is not None
    }

# Main extraction endpoint
@app.post("/api/v1/agents/extract", response_model=ExtractionResponse)
async def extract_entities(request: ExtractionRequest):
    """Extract entities from documents using Italian NER model + Gemini post-processing"""
    
    if not model_loaded:
        raise HTTPException(status_code=503, detail="NER model not ready")
    
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="No document IDs provided")
    
    try:
        all_texts = []
        processed_docs = []
        
        # Fetch text from all documents
        for doc_id in request.document_ids:
            try:
                text = await fetch_document_text(doc_id)
                if text.strip():  # Only add non-empty texts
                    all_texts.append(text)
                    processed_docs.append(doc_id)
            except Exception as e:
                logger.warning(f"Skipping document {doc_id}: {str(e)}")
                continue
        
        if not all_texts:
            raise HTTPException(
                status_code=404, 
                detail="No valid document texts found"
            )
        
        # Combine all texts for processing
        combined_text = "\n\n".join(all_texts)
        
        # Extract entities
        concatenated_entities, entity_results = extract_entities_from_text(combined_text)
        
        # Post-process with Gemini if query is provided
        structured_summary = None
        if request.query and concatenated_entities.strip():
            try:
                structured_summary = summarize_with_gemini(request.query, concatenated_entities)
            except Exception as e:
                logger.warning(f"Gemini post-processing failed: {e}")
                structured_summary = concatenated_entities
        
        return ExtractionResponse(
            success=True,
            agent_id=request.agent_id,
            document_ids=processed_docs,
            execution_id=request.execution_id,
            extracted_entities=concatenated_entities,
            entities_by_label=entity_results,
            structured_summary=structured_summary,
            message=f"Successfully extracted entities from {len(processed_docs)} documents" + 
                   (f" and processed with query: '{request.query}'" if request.query else "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

# Alternative endpoint for wrapper compatibility
@app.post("/api/v1/agents/process")
async def process_agent_task(request: dict):
    """Process agent task (orchestrator compatibility endpoint)"""
    
    agent_id = request.get("agentId")
    prompt = request.get("prompt", "")
    document_ids = request.get("documentIds", [])
    execution_id = request.get("executionId")
    
    # FIXED: Single validation that accepts both variations
    if agent_id not in ["extractor-agent", "extraction-agent"]:
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
    extraction_request = ExtractionRequest(
        document_ids=document_ids,
        agent_id=agent_id,
        execution_id=execution_id,
        query=prompt if prompt else None  # Use prompt as query
    )
    
    result = await extract_entities(extraction_request)
    
    return {
        "agentId": agent_id,
        "prompt": prompt,
        "documentIds": document_ids,
        "executionId": execution_id,
        "response": result.structured_summary if result.structured_summary else result.extracted_entities,
        "completedAt": None,  # Could add timestamp if needed
        "fullResult": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)