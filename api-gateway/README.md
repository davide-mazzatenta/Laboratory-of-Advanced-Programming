# API Gateway for Document Processing System

This service acts as the entry point for all requests to the document processing microservices, handling routing, authentication, and basic request preprocessing.

## Features

- **Centralized Routing**: Routes requests to appropriate backend services
- **Authentication**: Validates Supabase JWT tokens
- **CORS Support**: Configurable CORS settings for frontend integration
- **Request Logging**: Logs all incoming requests and their responses
- **Rate Limiting**: Prevents abuse through configurable rate limits
- **Error Handling**: Standardized error responses across services

## Requirements

- Java 17+
- Maven 3.8+
- Docker and Docker Compose for local development

## Local Development

### Building the Service

```bash
mvn clean package
```

### Running Locally with Docker

```bash
docker-compose -f docker-compose-apigateway.yml up
```

This will start the API Gateway along with all dependent services (document service, processing microservices, and LocalStack).

## Configuration

The service is configured through environment variables and Spring profiles:

- `SPRING_PROFILES_ACTIVE`: Set to `dev` for local development (default in Docker)
- `SUPABASE_JWT_ISSUER`: Your Supabase project URL
- `SUPABASE_JWK_URI`: Your Supabase JWKS URI (usually project URL + `/.well-known/jwks.json`)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins

## API Routes

All endpoints follow the pattern:

- `GET/POST/PUT/DELETE /api/v1/<service>/<endpoint>`

For example:

- Documents API: `/api/v1/documents/*`
- Collections API: `/api/v1/collections/*`
- Health check: `/api/health`

## Testing

When the API Gateway is running, you can test it using curl:

```bash
# Health check (no auth required)
curl http://localhost:8080/api/health

# List collections (requires auth)
curl -H "Authorization: Bearer YOUR_SUPABASE_JWT_TOKEN" http://localhost:8080/api/v1/collections
```

## Obtaining a Test Token from Supabase

To test authenticated endpoints locally:

1. Sign in to your Supabase project
2. Open the browser console on the Supabase dashboard
3. Run `localStorage.getItem('supabase.auth.token')` to get your token
4. Parse the returned JSON and use the `access_token` value

## Integrating with Frontend

Your frontend should include the JWT token in each request to the API Gateway:

```javascript
// Example fetch request
const response = await fetch('http://localhost:8080/api/v1/documents', {
  headers: {
    Authorization: `Bearer ${supabaseAccessToken}`,
  },
});
```

## Production Deployment

For AWS deployment, see the main project README for instructions using the Serverless Framework.
