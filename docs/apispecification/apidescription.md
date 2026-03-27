# 1 documents: pdf storage based on the only id and 1 table containing

the yml file containing the simple communication between
the frontend and the storage service:

basic doc memorizing functionality storage + retrieval based on simple ids and we will use supabase for all the databases so you just need to also design a super simple database schema for such user + project + project docs
each proj will have docs which will have titles and id and plain text content

-

for doc longer than 4000char (threshold can be modified) we will (on storage)chunk and embed chunks for that doc and store this again into supabase
on doc text request from agent side with a query if doc longer than threshold best sets of chunks will be returned

# agents:

frontend will call agent service with a simple prompt + ids (variable numb) of documents the user will select to attach to the prompt
the orchestrator will answer with a strategy ie a simple text answer explaining the plan

the frontend will answer again to either confirm ( so a bool?) or modify with additional instruction for the orchestrator

more precisely the interaction will always be between these services:
-orchestrator-agent(python container: will call the model) OA
-ochestration-service(springboot gateway on top of the python agent, should route all the request) OS
-api-gateway AG
-document-service DS
-other agents(accessible trhough api-gateway)

normal interaction:
-the frontend will call api-gateway with first prompt (intiaial prompt of user)+list of documents ids(selected from frontend)
-api-gateway route this request to the ochestrator-agent
-orchestrator-agent calls document service to retrieve text of all the included documents in the list (will go in the context of the orchestrator (translating for titles!!))
-orchestrator-agent will call the model internally to generate a plan out of the prompt once received answer from model frontend and api-gateway will go trough frontend to show the plan the the user

(optional step here: the user can even execute proposed plan or modify the structured prompt in some way)
-if user modify plan the structured prompt goes trough AG->OA to receive the STRUCTURED PROMPT

-after this the OA through OS and AG will call other agent that will return (async waiting) wile frontend poll the OS to see wheter we have result or not (important OA will use titles of document to prompt to each agent, OS will translate such titles into actual docids)
-after received the results from all the agents OA will return a small summary to frontend (small)

- structured results of what the agents proposed that will be printed on the canvas instead (OS should again handle this difference of passing)

so basically frontend will sync both with orchestration agent (to send the prompt and decide the plan) and with orchestrator service to receive docs produced from the agents

os should not do this full proxy, instead everything should be handled by orchestration agent (even the retrieval of docs given the id) using document-service + back and forth with frontend (via api gateway) on partial prompt

what os should do is just route requests w.r.t other agents
ie from oa to other agents handling format prompt + doc ids and receiving back the answer routing them both to frontend and to orchestration agent oa will create a summary and normally (as normal answer after last prompt plan return it to frontend (always via api gateway)
so it s in the communication with agents

apigateway modif
// SUGGESTED MODIFICATIONS TO EXISTING GatewayConfig.java

// ADD THESE NEW SERVICE URLs TO THE CLASS:

@Value("${services.orchestration-agent.url:http://localhost:8004}")
private String orchestrationAgentUrl;

@Value("${services.orchestration-service.url:http://localhost:8005}")
private String orchestrationServiceUrl;

// ADD THESE ROUTES TO THE customRouteLocator() METHOD BEFORE .build():

// ORCHESTRATION AGENT ROUTES - NEW (Frontend-facing)

// Plan creation
.route("orchestration_agent_plan", r -> r
.path("/api/v1/orchestrator/plan")
.and()
.method(HttpMethod.POST)
.filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
.uri(orchestrationAgentUrl))

// Plan modification
.route("orchestration_agent_plan_modify", r -> r
.path("/api/v1/orchestrator/plan/{planId}/modify")
.and()
.method(HttpMethod.POST)
.filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
.uri(orchestrationAgentUrl))

// Plan execution
.route("orchestration_agent_execute", r -> r
.path("/api/v1/orchestrator/plan/{planId}/execute")
.and()
.method(HttpMethod.POST)
.filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
.uri(orchestrationAgentUrl))

// Execution status polling
.route("orchestration_agent_status", r -> r
.path("/api/v1/orchestrator/execution/{executionId}/status")
.and()
.method(HttpMethod.GET)
.filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
.uri(orchestrationAgentUrl))

// Orchestration agent health check
.route("orchestration_agent_health", r -> r
.path("/api/v1/orchestrator/health")
.and()
.method(HttpMethod.GET)
.filters(f -> f
.setRequestHeader("X-Gateway-Source", "api-gateway")
.rewritePath("/api/v1/orchestrator/health", "/health"))
.uri(orchestrationAgentUrl))

// ORCHESTRATION SERVICE ROUTES - NEW (Agent-to-agent routing)

// Agent routing endpoint (for OA to call other agents through OS)
.route("agent_routing", r -> r
.path("/api/v1/agents/route")
.and()
.method(HttpMethod.POST)
.filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
.uri(orchestrationServiceUrl))

// ADDITIONAL AGENT ROUTES (if you add more agents later)
// These would be called by OS to route to specific agents

// Example: Analysis agent (when you add it)
// .route("analysis_agent", r -> r
// .path("/api/v1/agents/analyze")
// .and()
// .method(HttpMethod.POST)
// .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
// .uri("${services.analysis-agent.url:http://localhost:8006}"))

// Example: Visualization agent (when you add it)  
// .route("visualization_agent", r -> r
// .path("/api/v1/agents/visualize")
// .and()
// .method(HttpMethod.POST)
// .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
// .uri("${services.visualization-agent.url:http://localhost:8007}"))

/\*
ARCHITECTURE SUMMARY:

1. Frontend calls:
   - /api/v1/orchestrator/\* → Orchestration Agent (OA)

2. Orchestration Agent (OA) calls:
   - /api/v1/documents/\* → Document Service (DS)
   - /api/v1/agents/route → Orchestration Service (OS)

3. Orchestration Service (OS) routes to:
   - /api/v1/agents/extract → Extraction Agent
   - /api/v1/search → Search Agent
   - /api/v1/agents/analyze → Analysis Agent (future)
   - /api/v1/agents/visualize → Visualization Agent (future)

4. All communication goes through API Gateway for:
   - Centralized logging
   - Authentication/authorization
   - Rate limiting
   - CORS handling
   - Request/response transformation

DEPLOYMENT PORTS SUGGESTION:

- API Gateway: 8080
- Document Service: 8000
- Extraction Agent: 8001
- Search Agent: 8002
- Orchestration Agent: 8004
- Orchestration Service: 8005
- Analysis Agent: 8006 (future)
- Visualization Agent: 8007 (future)
  \*/

# Happy Path: Simplified Frontend-Backend Interaction Flow

## Phase 1: Plan Creation & Refinement (Sync with OA)

### Step 1: Initial Plan Request

```
Frontend → API Gateway → Orchestration Agent (OA)
```

**Frontend Call:**

```
POST /api/v1/orchestrator/plan
{
  "prompt": "Analyze financial performance of Q3 reports",
  "documentIds": ["doc1", "doc2", "doc3"],
  "userId": "user123",
  "projectId": "proj456"
}
```

**Internal OA Process:**

1. **OA** receives request with document IDs
2. **OA** calls Document Service via API Gateway to retrieve document texts:
   ```
   GET /api/v1/documents/{userId}/{projectId}/{docId}/text (for each doc)
   ```
3. **OA** analyzes prompt + document contents using AI model
4. **OA** generates execution strategy
5. **OA** stores plan internally and returns to Frontend

**Frontend Receives:**

```json
{
  "planId": "plan_789",
  "strategy": "I'll extract financial metrics from your Q3 reports using the extraction agent, then analyze trends with the analysis agent, and finally generate visualizations with the chart agent.",
  "estimatedSteps": 3,
  "documentTitles": ["Q3 Revenue Report", "Q3 Expenses", "Q3 Balance Sheet"]
}
```

### Step 2: Plan Modification (Optional, Iterative)

```
Frontend → API Gateway → Orchestration Agent (OA)
```

**Frontend Call:**

```
POST /api/v1/orchestrator/plan/plan_789/modify
{
  "additionalInstructions": "Focus specifically on profit margins and compare with Q2"
}
```

**Internal OA Process:**

1. **OA** retrieves stored plan context
2. **OA** calls AI model with original context + new instructions
3. **OA** generates refined strategy
4. **OA** updates plan and returns modified strategy

**Frontend Receives:**

```json
{
  "planId": "plan_789",
  "updatedStrategy": "I'll extract financial metrics focusing on profit margins, compare with Q2 data, then create comparative visualizations showing margin trends."
}
```

### Step 3: Plan Execution

```
Frontend → API Gateway → Orchestration Agent (OA)
```

**Frontend Call:**

```
POST /api/v1/orchestrator/plan/plan_789/execute
```

**Frontend Receives:**

```json
{
  "executionId": "exec_101",
  "status": "started",
  "message": "Execution started. I'll begin by extracting data from your documents."
}
```

## Phase 2: Asynchronous Execution with Agent Coordination

### Step 4: Execution Starts (Background)

**Internal OA Process:**

1. **OA** breaks down plan into agent-specific tasks
2. **OA** calls first agent through **OS** routing:

```
OA → OS (via internal call): POST /api/v1/agents/route
{
  "targetAgent": "extraction-agent",
  "agentPayload": {
    "prompt": "Extract profit margins and revenue data from Q3 Revenue Report",
    "documentIds": ["doc1"],
    "parameters": {
      "extractionType": "financial_metrics",
      "focus": "profit_margins"
    }
  }
}
```

3. **OS** routes to extraction agent via API Gateway
4. **OS** returns agent response to **OA**
5. **OA** processes result and continues with next agent

### Step 5: Frontend Polling (Async with Partial Results)

```
Frontend polls: API Gateway → Orchestration Agent (OA)
```

**Frontend Polling Call:**

```
GET /api/v1/orchestrator/execution/exec_101/status
```

**During Execution - Frontend Receives:**

```json
{
  "executionId": "exec_101",
  "status": "in_progress",
  "progress": {
    "completedAgents": 1,
    "totalAgents": 3,
    "currentAgent": "analysis-agent"
  },
  "partialResults": [
    {
      "agentName": "extraction-agent",
      "documentTitle": "Q3 Revenue Report",
      "taskDescription": "Extract profit margins and revenue data",
      "result": {
        "profit_margin_q3": 15.2,
        "revenue_q3": 2500000,
        "extracted_metrics": {
          "gross_margin": 15.2,
          "net_margin": 12.1,
          "revenue": 2500000,
          "costs": 2120000
        }
      },
      "status": "completed",
      "completedAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Step 6: Agent-to-Agent Coordination (Background)

**Internal Process continues:**

1. **OA** uses extraction results to enhance next agent prompt:

```
OA → OS: POST /api/v1/agents/route
{
  "targetAgent": "analysis-agent",
  "agentPayload": {
    "prompt": "Compare Q3 profit margin of 15.2% with Q2 data and analyze trends",
    "documentIds": ["doc1", "doc2"],
    "parameters": {
      "baseline_data": {
        "q3_margin": 15.2,
        "q3_revenue": 2500000
      },
      "comparison_period": "Q2"
    }
  }
}
```

2. **OS** routes to analysis agent, returns response to **OA**
3. **OA** continues with visualization agent using accumulated results

### Step 7: Execution Completion

**Final Status Poll - Frontend Receives:**

```json
{
  "executionId": "exec_101",
  "status": "completed",
  "progress": {
    "completedAgents": 3,
    "totalAgents": 3,
    "currentAgent": null
  },
  "partialResults": [
    {
      "agentName": "extraction-agent",
      "documentTitle": "Q3 Revenue Report",
      "taskDescription": "Extract profit margins and revenue data",
      "result": {
        /* extraction results */
      },
      "status": "completed",
      "completedAt": "2024-01-15T10:30:00Z"
    },
    {
      "agentName": "analysis-agent",
      "documentTitle": "Q3 vs Q2 Analysis",
      "taskDescription": "Compare quarterly margins and analyze trends",
      "result": {
        "trend_analysis": "Margin improvement of 2.4%",
        "key_factors": ["Reduced operational costs", "Increased efficiency"]
      },
      "status": "completed",
      "completedAt": "2024-01-15T10:35:00Z"
    },
    {
      "agentName": "visualization-agent",
      "documentTitle": "Trend Visualization",
      "taskDescription": "Create comparative charts",
      "result": {
        "chart_config": {
          /* chart data */
        },
        "visualization_type": "line_chart",
        "insights": "Clear upward trend in profitability"
      },
      "status": "completed",
      "completedAt": "2024-01-15T10:40:00Z"
    }
  ],
  "finalSummary": "Analysis complete: Q3 profit margins improved by 2.4% compared to Q2, driven by reduced operational costs and increased revenue efficiency. The trend shows consistent improvement in profitability.",
  "structuredResults": {
    "summary": "Q3 margins improved by 2.4% vs Q2",
    "visualizations": [
      {
        "type": "line_chart",
        "title": "Profit Margin Trend",
        "data": {
          /* chart configuration for canvas */
        }
      },
      {
        "type": "metrics_table",
        "title": "Key Financial Metrics",
        "data": {
          /* table data for canvas */
        }
      }
    ],
    "insights": [
      "Profit margins increased from 12.8% to 15.2%",
      "Revenue efficiency improved significantly",
      "Cost management strategies are working effectively"
    ]
  }
}
```

## Key Architectural Changes:

### Orchestration Agent (OA) Responsibilities:

- **Document Retrieval**: OA directly calls Document Service to get document content
- **AI Model Integration**: OA uses AI model for planning and summarization
- **Agent Coordination**: OA decides which agents to call and in what order
- **Context Management**: OA maintains execution context and passes relevant data between agents
- **Result Synthesis**: OA creates final summary and structures results for frontend display

### Orchestration Service (OS) Responsibilities:

- **Simple Routing**: OS only routes requests between OA and other agents
- **Format Handling**: OS handles request/response format translation if needed
- **Agent Discovery**: OS knows which agents are available and their endpoints

### Interaction Flow:

1. **Sync Phase**: Frontend ↔ OA (via AG) for planning
2. **Async Phase**: Frontend polls OA (via AG) while OA coordinates with agents through OS
3. **Agent Communication**: OA → OS → Target Agent → OS → OA

### Benefits of This Approach:

- **Simplified Architecture**: Clear separation of concerns
- **Better Context**: OA maintains full context across agent calls
- **Intelligent Routing**: OA can make smart decisions about agent sequence and parameters
- **Rich Results**: OA can synthesize results from multiple agents intelligently
