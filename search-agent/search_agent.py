import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import google.generativeai as genai
from tavily import TavilyClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TAVILY_API_KEY = "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"
SERPER_API_KEY = "be6ccf9ec3eaff009a633de46aca91d0d348b7f4"

# Gemini API keys with fallback mechanism
GEMINI_API_KEYS = [
    "AIzaSyBEsyakskQ7iZnDfnlDGQYwSB0QQJ5fMhA",
    "AIzaSyAEEjrZnXFKR-uonJWnt46iPYdNLQzSqVI",
    "AIzaSyCDQBZ50InkrXIkHI7C0p_Xzg1wjroTUkQ"
]

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    include_sources: Optional[bool] = True

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str

class SearchResponse(BaseModel):
    query: str
    summary: str
    sources: List[SearchResult]
    search_providers_used: List[str]

class SearchAgent:
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        self.current_gemini_key_index = 0
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure Gemini with current API key"""
        try:
            genai.configure(api_key=GEMINI_API_KEYS[self.current_gemini_key_index])
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info(f"Configured Gemini with key index {self.current_gemini_key_index}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
            raise
    
    def _try_next_gemini_key(self):
        """Switch to next Gemini API key"""
        self.current_gemini_key_index = (self.current_gemini_key_index + 1) % len(GEMINI_API_KEYS)
        self._configure_gemini()
        logger.info(f"Switched to Gemini key index {self.current_gemini_key_index}")
    
    async def search_with_tavily(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search using Tavily API"""
        try:
            logger.info(f"Searching with Tavily: {query}")
            response = self.tavily_client.search(
                query=query,
                search_depth="basic",
                max_results=max_results
            )
            
            results = []
            for result in response.get("results", []):
                results.append(SearchResult(
                    url=result.get("url", ""),
                    title=result.get("title", ""),
                    snippet=result.get("content", "")
                ))
            
            logger.info(f"Tavily returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []
    
    async def search_with_serper(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search using Serper API"""
        try:
            logger.info(f"Searching with Serper: {query}")
            
            async with httpx.AsyncClient() as client:
                payload = {
                    "q": query,
                    "num": max_results
                }
                headers = {
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    "https://google.serper.dev/search",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for result in data.get("organic", []):
                    results.append(SearchResult(
                        url=result.get("link", ""),
                        title=result.get("title", ""),
                        snippet=result.get("snippet", "")
                    ))
                
                logger.info(f"Serper returned {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []
    
    async def summarize_with_gemini(self, query: str, results: List[SearchResult]) -> str:
        """Summarize search results using Gemini with fallback mechanism"""
        if not results:
            return "No search results found to summarize."
        
        # Prepare context from search results
        search_context = "\n\n".join([
            f"Source: {result.title}\nURL: {result.url}\nContent: {result.snippet}"
            for result in results[:10]  # Limit to top 10 results
        ])
        
        prompt = f"""Basandoti sui seguenti risultati dal web per la domanda "{query}", fornisci uno strutturato riassunto:

{search_context}

Fornisci:
1. Un chiaro sommario conciso che comprende ogni risultato dal più al meno rilevante per la domanda (giusto qualche frase per quelle meno rilevanti)
2. la risposta deve essere unica l'utente non deve sapere che ricevi molte fonti
3. sei un ricercatore su ambito giuridico se si tratta di articoli o sentenze cita tale fonte all interno di [] es. 

Keep the summary informative but concise, and ensure it directly addresses the original query."""

        # Try each Gemini API key until one works
        for attempt in range(len(GEMINI_API_KEYS)):
            try:
                logger.info(f"Attempting Gemini summarization with key index {self.current_gemini_key_index}")
                
                response = self.model.generate_content(
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
                    self._try_next_gemini_key()
                else:
                    logger.error("All Gemini API keys failed")
                    return self._fallback_summary(query, results)
        
        return self._fallback_summary(query, results)
    
    def _fallback_summary(self, query: str, results: List[SearchResult]) -> str:
        """Fallback summary when Gemini fails"""
        if not results:
            return f"Search completed for '{query}' but no results were found."
        
        summary = f"Search Results for '{query}':\n\n"
        for i, result in enumerate(results[:5], 1):
            summary += f"{i}. {result.title}\n   {result.snippet[:200]}...\n   Source: {result.url}\n\n"
        
        return summary
    
    async def search_and_summarize(self, query: str, max_results: int = 5) -> SearchResponse:
        """Main method to search using both providers and summarize results"""
        logger.info(f"Starting search and summarization for: {query}")
        
        # Search with both providers concurrently
        tavily_task = self.search_with_tavily(query, max_results)
        serper_task = self.search_with_serper(query, max_results)
        
        tavily_results, serper_results = await asyncio.gather(
            tavily_task, serper_task, return_exceptions=True
        )
        
        # Handle exceptions and combine results
        all_results = []
        providers_used = []
        
        if isinstance(tavily_results, list):
            all_results.extend(tavily_results)
            providers_used.append("tavily")
        else:
            logger.error(f"Tavily search failed: {tavily_results}")
        
        if isinstance(serper_results, list):
            all_results.extend(serper_results)
            providers_used.append("serper")
        else:
            logger.error(f"Serper search failed: {serper_results}")
        
        if not all_results:
            raise HTTPException(status_code=503, detail="All search providers failed")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Limit to max_results
        unique_results = unique_results[:max_results]
        
        # Summarize with Gemini
        summary = await self.summarize_with_gemini(query, unique_results)
        
        return SearchResponse(
            query=query,
            summary=summary,
            sources=unique_results,
            search_providers_used=providers_used
        )

# Global search agent instance
search_agent = SearchAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Search Agent starting up...")
    yield
    logger.info("Search Agent shutting down...")

# FastAPI app
app = FastAPI(
    title="Search Agent Service",
    description="Lightweight search agent using Tavily, Serper, and Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "search-agent",
        "gemini_key_index": search_agent.current_gemini_key_index
    }

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_endpoint(request: SearchRequest):
    """Main search endpoint"""
    try:
        logger.info(f"Received search request: {request.query}")
        
        result = await search_agent.search_and_summarize(
            query=request.query,
            max_results=request.max_results
        )
        
        logger.info(f"Search completed successfully for: {request.query}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/search/status")
async def search_status():
    """Get search agent status"""
    return {
        "tavily_configured": bool(TAVILY_API_KEY and TAVILY_API_KEY != "tvly-YOUR_TAVILY_API_KEY_HERE"),
        "serper_configured": bool(SERPER_API_KEY and SERPER_API_KEY != "your_serper_api_key_here"),
        "gemini_keys_available": len(GEMINI_API_KEYS),
        "current_gemini_key_index": search_agent.current_gemini_key_index
    }

if __name__ == "__main__":
    uvicorn.run(
        "search_agent:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )