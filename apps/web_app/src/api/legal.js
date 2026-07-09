import axios from 'axios';

/** GET /legal/posts — Fetch lawyer feed timeline */
export async function getPosts() {
  const res = await axios.get('/legal/posts');
  return res.data;
}

/** POST /legal/posts — Publish a new feed post */
export async function createPost(content) {
  const res = await axios.post('/legal/posts', { content });
  return res.data;
}

/** POST /legal/voice-query — Text or voice legal query */
export async function voiceQuery(formData) {
  const res = await axios.post('/legal/voice-query', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/** POST /legal/analyze-document — Analyze uploaded PDF/doc */
export async function analyzeDocument(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await axios.post('/legal/analyze-document', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/** POST /legal/cases/request — Client submits a case consultation */
export async function submitCaseRequest(lawyerId, querySummary, docIds = []) {
  const res = await axios.post('/legal/cases/request', {
    lawyer_id: lawyerId,
    user_query_summary: querySummary,
    attached_document_ids: docIds,
  });
  return res.data;
}

/** POST /legal/cases/resolve — Lawyer accepts or declines a case */
export async function resolveCase(caseId, action) {
  const res = await axios.post('/legal/cases/resolve', {
    case_id: caseId,
    action, // 'accept' | 'decline'
  });
  return res.data;
}

/** PATCH /legal/cases/{caseId}/stage — Lawyer updates case stage */
export async function updateCaseStage(caseId, newStage) {
  const res = await axios.patch(`/legal/cases/${caseId}/stage`, {
    new_stage: newStage,
  });
  return res.data;
}

/** GET /legal/cases — Fetch user's cases */
export async function getCases() {
  const res = await axios.get('/legal/cases');
  return res.data;
}

/** GET /legal/lawyers — Fetch verified lawyer directory */
export async function getLawyers(filters = {}) {
  const res = await axios.get('/legal/lawyers', { params: filters });
  return res.data;
}

const CORE_API_BASE = import.meta.env.VITE_CORE_API_URL || (import.meta.env.PROD ? 'https://core-api-584212158273.asia-south1.run.app' : '/core-api');

/** POST /chat — Conversational Legal Advice */
export async function askLexAI(query, sessionId = null, limit = 5) {
  const res = await fetch(`${CORE_API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      session_id: sessionId,
      limit,
    }),
  });
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

/** GET /sessions — Get active chat sessions */
export async function getLexAISessions() {
  const res = await fetch(`${CORE_API_BASE}/sessions`);
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

/** POST /brief/{case_id} — Generate case brief */
export async function getCaseBrief(caseId) {
  const res = await fetch(`${CORE_API_BASE}/brief/${caseId}`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
}

