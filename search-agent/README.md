# Search Agent Service

A lightweight microservice that provides intelligent web search capabilities using Tavily and Serper APIs, with AI-powered summarization via Google Gemini.

## Features

- **Dual Search Providers**: Uses both Tavily and Serper APIs for comprehensive search coverage
- **AI Summarization**: Leverages Google Gemini 1.5 Flash for intelligent result summarization
- **Fallback Mechanism**: Multiple Gemini API keys with automatic failover
- **Deduplication**: Removes duplicate URLs from combined search results
- **RESTful API**: FastAPI-based service with automatic OpenAPI documentation
- **Health Monitoring**: Built-in health checks and status endpoints
- **Docker Optimized**: Lightweight container (~200MB) with minimal resource usage

## API Endpoints

### POST /api/v1/search

Main search endpoint that queries both Tavily and Serper, then summarizes results.

**Request Body:**

```json
{
  "query": "artificial intelligence trends 2025",
  "max_results": 5,
  "include_sources": true
}
```

**Response:**

```json
{
  "query": "artificial intelligence trends 2025",
  "summary": "AI-generated summary of search results...",
  "sources": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "snippet": "Article snippet..."
    }
  ],
  "search_providers_used": ["tavily", "serper"]
}
```

### GET /health

Health check endpoint for container orchestration.

### GET /api/v1/search/status

Returns configuration status and API key availability.

## Configuration

Replace the placeholder API keys in `search_agent.py`:

```python
TAVILY_API_KEY = "tvly-YOUR_ACTUAL_TAVILY_KEY"
SERPER_API_KEY = "your_actual_serper_key"
GEMINI_API_KEYS = [
    "your_primary_gemini_key",
    "your_backup_gemini_key_1",
    "your_backup_gemini_key_2"
]
```

## Getting API Keys

1. **Tavily API**: Sign up at [tavily.com](https://tavily.com) for free tier
2. **Serper API**: Get your key at [serper.dev](https://serper.dev)
3. **Google Gemini**: Obtain from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest test.py -v

# Start the service locally
python search_agent.py
```

### Docker Build

```bash
# Build the container
docker build -t search-agent .

# Run locally
docker run -p 8002:8002 search-agent
```

## Integration with Orchestrator

The search agent integrates seamlessly with your existing microservices architecture. The orchestrator can call the search endpoint like this:

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://api-gateway:8080/api/v1/search",
        json={"query": "latest AI research", "max_results": 10}
    )
    search_results = response.json()
    summary = search_results["summary"]
```

## Resource Usage

- **Memory**: ~256-512MB (minimal footprint)
- **CPU**: ~0.25-0.5 cores (efficient async processing)
- **Network**: Only outbound requests to search APIs
- **Storage**: Stateless service, no persistent storage needed

## Error Handling

- Automatic retry with different Gemini API keys
- Graceful degradation when search providers fail
- Comprehensive logging for debugging
- Proper HTTP status codes and error messages

## Security

- No sensitive data stored in container
- API keys should be injected via environment variables in production
- CORS properly configured for your frontend origins
- Non-root user execution in container
