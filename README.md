# Multiagent Platform API Gateway Architecture

## Overview

This document describes a simple API gateway architecture for a multiagent platform that handles document management and agent orchestration through Spring Boot microservices.

## System Components

### 1. Document Storage Service

**Purpose**: Manage PDF document storage and retrieval using simple composite identifiers.

**Key Features**:

- Store raw PDF files in Supabase database
- Extract and store plain text content for agent processing
- Use composite ID format: `userId_projectId_docId`
- Support document listing by project

**Database Tables**:

- `pdf_storage`: Binary PDF data storage
- `project_documents`: Metadata and extracted text content

### 2. Agent Orchestrator Service

**Purpose**: Coordinate multi-agent workflows through an intelligent orchestration system.

**Workflow Process**:

1. **Planning Phase**: Frontend sends prompt + document IDs → Orchestrator generates strategy
2. **Confirmation Phase**: User confirms or modifies the plan iteratively
3. **Execution Phase**: Orchestrator distributes tasks to individual agents
4. **Response Phase**: Agents process tasks and return results

## API Workflows

### Document Management Flow

```
Frontend → API Gateway → Storage Service
1. Upload PDF with userId/projectId/docId
2. Store binary data + extract text content
3. Return success confirmation

Frontend → API Gateway → Storage Service
1. Request document by composite ID
2. Retrieve raw PDF or document metadata
3. Return requested data
```

### Agent Orchestration Flow

```
Frontend → API Gateway → Orchestrator
1. POST /orchestrator/plan (prompt + document IDs)
2. Receive strategy proposal

Frontend → API Gateway → Orchestrator
3. POST /orchestrator/plan/{planId}/confirm (confirm/modify)
4. Iterate until plan is confirmed

Frontend → API Gateway → Orchestrator
5. POST /orchestrator/execute (execute confirmed plan)

API Gateway → Individual Agent Services
6. POST /agents/process (agent-specific tasks)
7. Collect responses and compile final result
```

## Database Schema

### Core Tables

- **pdf_storage**: Raw PDF binary data with composite IDs
- **project_documents**: Document metadata and plain text content
- **execution_plans**: Track orchestration strategies (optional)
- **execution_results**: Store agent responses and final results (optional)

### ID Structure

All documents use composite IDs in format: `userId_projectId_docId`

- Enables simple partitioning and access control
- Supports project-level document organization
- Allows for easy user data isolation

## Configuration Requirements

### Environment Variables for Agents

Agent services should be configured via environment variables:

```
AGENT_1_ID=research_agent
AGENT_2_ID=analysis_agent
AGENT_3_ID=summary_agent
```

# Full stack (all services including chunker and extraction agent)

./run-stack.sh full up

# OR

docker-compose -f docker-compose.yml -f docker-compose.full.yml up -d

# Without chunker service (but with extraction agent)

./run-stack.sh no-chunker up

# OR

docker-compose -f docker-compose.yml -f docker-compose.no-chunker.yml up -d

# Without extraction agent (but with chunker)

./run-stack.sh no-extraction up

# OR

docker-compose -f docker-compose.yml -f docker-compose.no-extraction.yml up -d

# Minimal stack (without chunker and extraction agent)

./run-stack.sh minimal up

# OR

docker-compose up -d

# Build specific configuration

./run-stack.sh full build
./run-stack.sh no-chunker build

# Stop services

./run-stack.sh full down

# View logs

./run-stack.sh full logs
