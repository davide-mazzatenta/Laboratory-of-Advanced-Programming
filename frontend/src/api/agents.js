// frontend/src/api/agents.js
const API_BASE = (
  (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL)
    ? process.env.REACT_APP_API_URL
    : window.location.origin
).replace(/\/+$/, '');

async function http(method, path, body, extraHeaders = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...extraHeaders },
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { /* keep text */ }

  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || text || res.statusText;
    throw new Error(msg);
  }
  return data ?? {};
}

// Usato in AgentsPage per il badge di stato
export async function testOrchestrationService() {
  try {
    const r = await http('GET', '/api/health');
    // considera healthy se lo dice esplicitamente o se la chiamata va a buon fine
    return r?.status === 'healthy' || r?.ok === true || true;
  } catch {
    return false;
  }
}

// Usato in AgentsPage per inviare il prompt
export async function sendOrchestrationMessage(prompt, documentIds = [], userId, projectId, executionId) {
  if (!prompt || !Array.isArray(documentIds) || documentIds.length === 0) {
    throw new Error('prompt e documentIds sono obbligatori');
  }

  const payload = {
    prompt,
    document_ids: documentIds,
    agent_id: 'orchestration-agent',
    execution_id: executionId,
    user_id: userId,
    project_id: projectId,
  };

  // Prova prima il path più “parlante”, poi fallback
  let resp;
  let lastErr;
  for (const p of [
    '/api/orchestration/agents/orchestrate',
    '/api/agents/orchestrate',
  ]) {
    try {
      resp = await http('POST', p, payload, executionId ? { 'X-Execution-Id': executionId } : {});
      lastErr = null;
      break;
    } catch (e) {
      lastErr = e;
    }
  }
  if (!resp && lastErr) throw lastErr;

  const content =
    resp?.content ||
    resp?.final_response ||
    resp?.message ||
    (typeof resp === 'string' ? resp : JSON.stringify(resp));

  return {
    content,
    agentId: resp?.agent_id || resp?.agentId || 'orchestration-agent',
    executionId: resp?.execution_id || resp?.executionId,
  };
}
