# Orchestration Agent Service

AI Legal Assistant that coordinates multiple specialized agents for complex legal document analysis using Google Gemini.

## Overview

The Orchestration Agent serves as the central intelligence that:

1. **Analyzes** user legal queries and available documents
2. **Plans** optimal sequences of agent actions
3. **Coordinates** execution across multiple specialized agents
4. **Synthesizes** results into comprehensive legal responses

## Architecture

```
Frontend → API Gateway → Orchestration Agent → [Search/Extract/Generation Agents]
                                              ↓
                                         Document Service
```

## Agent Coordination

The orchestration agent can coordinate these specialized agents:

### Available Agents

- **Search Agent** (`/api/v1/agents/search`): Legal research, case law, regulations
- **Extraction Agent** (`/api/v1/agents/process`): Entity extraction, data mining from documents
- **Generation Agent** (`/api/v1/agents/process`): Document analysis, summarization, regeneration

### Workflow Strategy

1. **Search First**: For external legal context (case law, regulations)
2. **Extract Data**: For specific information from documents
3. **Generate Analysis**: For synthesis and final legal advice

## API Endpoints

### Health Check

```bash
GET /health
```

Response:

```json
{
  "status": "healthy",
  "service": "orchestration-agent",
  "gemini_configured": true,
  "service_ready": true
}
```

### Main Orchestration Endpoint

```bash
POST /api/v1/agents/orchestrate
```

Request body:

```json
{
  "document_ids": ["userId_projectId_docId1", "userId_projectId_docId2"],
  "prompt": "Analyze these contracts for termination risks and provide recommendations",
  "agent_id": "orchestration-agent",
  "execution_id": "optional-execution-id"
}
```

Response:

```json
{
  "success": true,
  "agent_id": "orchestration-agent",
  "execution_id": "optional-execution-id",
  "prompt": "User's legal query",
  "document_ids": ["doc1", "doc2"],
  "actions_taken": [
    {
      "turn": 1,
      "action": {
        "action_type": "search",
        "query": "contract termination law precedents"
      },
      "result": "Search results..."
    }
  ],
  "final_response": "Comprehensive legal analysis...",
  "message": "Successfully orchestrated 3 actions across 2 documents"
}
```

## How It Works

### 1. Document Preparation

- Fetches documents using Document Service API
- Extracts titles and first lines for context
- Creates document inventory for agent coordination

### 2. Intelligent Planning

- Uses Gemini with specialized legal system prompt
- Analyzes query complexity and document requirements
- Plans optimal agent execution sequence

### 3. Action Execution

The orchestrator can execute these action types:

#### Search Action

```json
{ "action_type": "search", "query": "contract law termination clauses" }
```

Calls: `POST {SEARCH_AGENT_URL}/api/v1/agents/search`

#### Extraction Action

```json
{
  "action_type": "extract",
  "query": "extract termination clauses and dates",
  "document_titles": ["Contract A", "Contract B"]
}
```

Calls: `POST {EXTRACTION_AGENT_URL}/api/v1/agents/process`

#### Generation Action

```json
{
  "action_type": "generate",
  "query": "analyze termination risks",
  "document_titles": ["Contract A"],
  "full_doc": false
}
```

Calls: `POST {GENERATION_AGENT_URL}/api/v1/agents/process`

### 4. Multi-Turn Coordination

- Executes up to 3 planning turns
- Each turn can contain multiple actions
- Results feed into next turn's planning
- Final synthesis provides comprehensive response

## Integration Points

### Frontend Integration

```javascript
// Frontend calls orchestration via API Gateway
const response = await fetch('/api/v1/orchestration/orchestrate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    document_ids: ['user_project_doc1', 'user_project_doc2'],
    prompt: 'What are the legal risks in these contracts?',
  }),
});
```

### Service Dependencies

- **Document Service**: Document content retrieval
- **Search Agent**: Legal research capabilities
- **Extraction Agent**: Structured data extraction
- **Generation Agent**: Content analysis and generation

## Environment Variables

```bash
DOCUMENT_SERVICE_URL=http://document-service:8000
EXTRACTION_AGENT_URL=http://extraction-agent:8001
SEARCH_AGENT_URL=http://search-agent:8002
GENERATION_AGENT_URL=http://generation-agent:8003
```

## Error Handling

- **Service Unavailable (503)**: When Gemini or dependent services fail
- **Bad Request (400)**: Invalid document IDs or missing prompts
- **Not Found (404)**: When no documents can be retrieved
- **Bad Gateway (502)**: When downstream services fail

## Security Features

- Non-root container execution
- Input validation and sanitization
- Timeout protection for external calls
- API key rotation support for Gemini

## Performance Considerations

- **Lightweight**: No heavy ML models (uses external Gemini API)
- **Async Operations**: Non-blocking I/O for agent coordination
- **Resource Limits**: 512M memory, 0.5 CPU allocation
- **Timeouts**: 30s document fetch, 60s search, 120s extract/generate

## Testing

Run unit tests:

```bash
python test.py [orchestration_url] [test_document_id]
```

## Legal Assistant Capabilities

The orchestration agent specializes in:

- **Contract Analysis**: Terms, risks, compliance issues
- **Document Review**: Due diligence, regulatory compliance
- **Legal Research**: Case law, statute analysis
- **Risk Assessment**: Liability, regulatory exposure
- **Document Generation**: Legal summaries, recommendations
