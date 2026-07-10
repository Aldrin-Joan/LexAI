/**
 * Legal API client — authenticated calls to the backend legal router.
 *
 * All functions that communicate with the core_api backend attach the
 * Firebase ID token as a Bearer token in the Authorization header.
 *
 * Usage:
 *   import { getCases, submitCaseRequest, ... } from './legal';
 *   // token comes from: const { token } = useAuth();
 */

import axios from 'axios';

/** Base URL for the deployed Core API (falls back to Vite dev proxy). */
const CORE_API_BASE =
  import.meta.env.VITE_CORE_API_URL ||
  (import.meta.env.PROD
    ? 'https://core-api-584212158273.asia-south1.run.app'
    : '');

// ---------------------------------------------------------------------------
// Shared helper
// ---------------------------------------------------------------------------

/**
 * Build an Axios config object with the Firebase ID token attached.
 *
 * @param {string} token - Firebase ID token from useAuth().token.
 * @param {object} [extra] - Additional Axios config overrides.
 * @returns {object} Axios config with Authorization header.
 */
function authConfig(token, extra = {}) {
  return {
    headers: { Authorization: `Bearer ${token}` },
    ...extra,
  };
}

// ---------------------------------------------------------------------------
// Advocate Feed
// ---------------------------------------------------------------------------

/**
 * Fetch paginated advocate feed posts.
 *
 * @param {string} token - Firebase ID token.
 * @param {object} [params]
 * @param {number} [params.limit=20] - Max posts to return.
 * @param {number} [params.offset=0] - Pagination offset.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function getPosts(token, { limit = 20, offset = 0 } = {}) {
  const res = await axios.get('/legal/posts', {
    ...authConfig(token),
    params: { limit, offset },
  });
  return res.data;
}

/**
 * Publish a new feed post (verified advocates only).
 *
 * @param {string} token - Firebase ID token.
 * @param {string} content - Post body text.
 * @returns {Promise<object>} The newly created post record.
 */
export async function createPost(token, content) {
  const res = await axios.post(
    '/legal/posts',
    { content },
    authConfig(token),
  );
  return res.data;
}

// ---------------------------------------------------------------------------
// Case Management
// ---------------------------------------------------------------------------

/**
 * Fetch the caller's own cases (token-scoped, no user_id param needed).
 *
 * @param {string} token - Firebase ID token.
 * @param {object} [params]
 * @param {number} [params.limit=10] - Max cases to return.
 * @param {number} [params.offset=0] - Pagination offset.
 * @returns {Promise<Array>} Array of case objects.
 */
export async function getCases(token, { limit = 10, offset = 0 } = {}) {
  const res = await axios.get('/legal/cases', {
    ...authConfig(token),
    params: { limit, offset },
  });
  return res.data;
}

/**
 * Submit a new consultation case request.
 *
 * client_id is automatically populated server-side from the token —
 * it is NOT sent in the request body.
 *
 * @param {string} token - Firebase ID token.
 * @param {object} payload
 * @param {string} payload.lawyerId - Firebase UID of the target advocate.
 * @param {string} payload.lawyerName - Display name of the advocate.
 * @param {string} payload.querySummary - Client's case description.
 * @param {string[]} [payload.docIds=[]] - IDs of attached documents.
 * @returns {Promise<object>} The newly created case record.
 */
export async function submitCaseRequest(
  token,
  { lawyerId, lawyerName, querySummary, docIds = [] },
) {
  const res = await axios.post(
    '/legal/cases/request',
    {
      lawyer_id: lawyerId,
      lawyer_name: lawyerName,
      user_query_summary: querySummary,
      attached_document_ids: docIds,
    },
    authConfig(token),
  );
  return res.data;
}

/**
 * Accept or decline a pending case request (assigned lawyer only).
 *
 * @param {string} token - Firebase ID token.
 * @param {number} caseId - Database ID of the case.
 * @param {'accept'|'decline'} action - Resolution action.
 * @returns {Promise<object>} Updated case record.
 */
export async function resolveCase(token, caseId, action) {
  const res = await axios.post(
    '/legal/cases/resolve',
    { case_id: caseId, action },
    authConfig(token),
  );
  return res.data;
}

/**
 * Advance a case to the next workflow stage (assigned lawyer only).
 *
 * @param {string} token - Firebase ID token.
 * @param {number} caseId - Database ID of the case.
 * @param {string} newStage - Target CaseStage enum value.
 * @returns {Promise<object>} Updated case record.
 */
export async function updateCaseStage(token, caseId, newStage) {
  const res = await axios.patch(
    `/legal/cases/${caseId}/stage`,
    { new_stage: newStage },
    authConfig(token),
  );
  return res.data;
}

// ---------------------------------------------------------------------------
// Peer-to-Peer Chat
// ---------------------------------------------------------------------------

/**
 * Fetch the message thread between the caller and a contact.
 *
 * @param {string} token - Firebase ID token.
 * @param {string} contactId - Firebase UID of the other party.
 * @param {object} [params]
 * @param {number} [params.limit=50] - Max messages to return.
 * @param {number} [params.offset=0] - Pagination offset.
 * @returns {Promise<Array>} Array of message objects, oldest first.
 */
export async function getChatHistory(
  token,
  contactId,
  { limit = 50, offset = 0 } = {},
) {
  const res = await axios.get('/legal/chat/history', {
    ...authConfig(token),
    params: { contact_id: contactId, limit, offset },
  });
  return res.data;
}

/**
 * Send a message via REST — fallback when the WebSocket is disconnected.
 *
 * This call is idempotent: resending with the same client_msg_id returns
 * 200 with the existing record rather than an error.
 *
 * @param {string} token - Firebase ID token.
 * @param {object} payload
 * @param {string} payload.receiverId - Firebase UID of the recipient.
 * @param {string} payload.content - Message text.
 * @param {string} payload.clientMsgId - Client-generated UUID.
 * @returns {Promise<object>} Persisted message record.
 */
export async function sendChatMessage(
  token,
  { receiverId, content, clientMsgId },
) {
  const res = await axios.post(
    '/legal/chat/send',
    {
      receiver_id: receiverId,
      content,
      client_msg_id: clientMsgId,
    },
    authConfig(token),
  );
  return res.data;
}

/**
 * Fetch the directory of verified advocates.
 *
 * @param {string} token - Firebase ID token.
 * @returns {Promise<Array>} List of lawyer profile objects.
 */
export async function getLawyers(token) {
  const res = await axios.get('/legal/lawyers', authConfig(token));
  return res.data;
}


// ---------------------------------------------------------------------------
// LexAI  (deployed Core API — separate service, no local auth proxy)
// ---------------------------------------------------------------------------

/**
 * Send a legal research query to the LexAI RAG engine.
 *
 * @param {string} query - Natural-language legal question.
 * @param {string|null} [sessionId=null] - Existing session ID for context.
 * @param {number} [limit=5] - Number of RAG precedent results to return.
 * @returns {Promise<{answer: string, precedents: Array}>} AI response.
 */
export async function askLexAI(query, sessionId = null, limit = 5) {
  const res = await fetch(`${CORE_API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId, limit }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

/**
 * Fetch active LexAI chat sessions.
 *
 * @returns {Promise<Array>} List of active session records.
 */
export async function getLexAISessions() {
  const res = await fetch(`${CORE_API_BASE}/sessions`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

/**
 * Generate a legal case brief for a given case ID.
 *
 * @param {string} caseId - Case identifier.
 * @returns {Promise<object>} Generated brief.
 */
export async function getCaseBrief(caseId) {
  const res = await fetch(`${CORE_API_BASE}/brief/${caseId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}
