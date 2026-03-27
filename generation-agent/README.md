Generation Agent Components:

main.py - The main FastAPI service that:

Uses Gemini for text generation (same API key pattern as your extraction agent)
Calls document service to fetch content based on query/full_doc flag
Handles both single chunk and multi-chunk generation
Supports both /api/v1/agents/generate and /api/v1/agents/process endpoints for orchestrator compatibility

Dockerfile - Lightweight container (no heavy ML models, just Gemini API calls)
test.py - Comprehensive test suite that validates different generation scenarios
Updated docker-compose.yml - Adds the generation-agent service on port 8003

Key Features:
The agent flow works exactly as you specified:

Receives query + document_id + full_doc (boolean)
If full_doc=false: Calls document service with query to get relevant chunks
If full_doc=true: Calls document service to get full document or all chunks
Passes content to Gemini for generation
Returns generated content to orchestrator

Document Service Modifications:
I've provided the necessary modifications to handle the full document case:

New endpoint: /api/v1/documents/{user_id}/{project_id}/{doc_id}/chunks - Gets all chunks for a document
Modified existing endpoint: Added full_chunks parameter to the text endpoint
New database method: get_all_chunks() to retrieve all chunks from database

Usage Examples:
bash# Query-based generation (gets relevant chunks)
POST /api/v1/agents/generate
{
"document_id": "user_project_doc",
"query": "Summarize the main points",
"full_doc": false
}

# Full document generation (gets all content)

POST /api/v1/agents/generate
{
"document_id": "user_project_doc",
"query": "Create a comprehensive analysis",
"full_doc": true
}
