# NyayGraph: Legal RAG API Technical Manual

This document provides a deep-dive into the REST API endpoints, detailed request/response schemas, and 5 distinct examples for each operation.

## Base URL

- **Local Development**: `http://localhost:7860`
- **Public Testing (Ngrok)**: `https://willy-segmentary-superinnocently.ngrok-free.dev`
- **Cloud (Hugging Face)**: `https://[your-space].hf.space`

---

## 1. Hybrid Retrieval Endpoint (`/search`)
The core retrieval engine combining Sparse (BM25), Dense (MPNet), and Graph (PageRank) signals.

### Specification
- **Method**: `POST`
- **Path**: `/search`
- **Request Body**:
    - `query` (string, Required): The legal query or case title.
    - `limit` (number, Default 5): Max results to return.
    - `mode` (string): `keyword`, `semantic`, `graph`, `hybrid`, `ultra`.

### Search Modes Explained
| Mode | Signal Used | Best For |
| :--- | :--- | :--- |
| `keyword` | BM25 on Titles/Body | Finding specific case names or statutes. |
| `semantic` | MPNet Embeddings | Broad legal concepts (e.g., "custodial torture"). |
| `graph` | PageRank Popularity | Finding the most authoritative/cited precedents. |
| `hybrid` | RRF (Weighted) | **Production Default.** High recall/precision balance. |
| `ultra` | Hybrid + Re-ranker | Maximum accuracy for complex queries. |

### 5 Detailed Examples

1. **Specific Citation Search**
   ```bash
   curl -X POST http://localhost:7860/search -d '{"query": "D.K. Basu v. State of West Bengal", "mode": "keyword"}'
   ```
   *Objective: Quick retrieval of a known landmark case.*

2. **Concept Discovery (Semantic)**
   ```bash
   curl -X POST http://localhost:7860/search -d '{"query": "rights of women in ancestral property", "mode": "semantic"}'
   ```
   *Objective: Find cases related to the conceptual legal point regardless of terminology.*

3. **High-Authority Sourcing (Graph)**
   ```bash
   curl -X POST http://localhost:7860/search -d '{"query": "Freedom of Speech Article 19", "mode": "graph", "limit": 3}'
   ```
   *Objective: Retrieve the most 'important' (highly cited) cases on speech.*

4. **Complex Legal Query (Hybrid)**
   ```bash
   curl -X POST http://localhost:7860/search -d '{"query": "validity of arbitration clause in unstamped agreement", "mode": "hybrid"}'
   ```
   *Objective: Standard RAG retrieval for specific legal intersections.*

5. **Precision-Critical Audit (Ultra)**
   ```bash
   curl -X POST http://localhost:7860/search -d '{"query": "Section 482 CrPC quashing of FIR for commercial disputes", "mode": "ultra"}'
   ```
   *Objective: Use the Cross-Encoder to find only the most relevant judicial opinions.*

---

## 2. Conversational RAG Endpoint (`/chat`)
Generative legal advice grounded in the 1,000 indexed case bodies (Progressively scaling to 26,000).

### Specification
- **Method**: `POST`
- **Path**: `/chat`
- **Request Body**:
    - `query` (string, Required): User question.
    - `session_id` (string, Optional): UUID to maintain conversational state.

### 5 Interaction Examples

1. **Turn 1: Legal Opinion Request**
   ```bash
   curl -X POST http://localhost:7860/chat -d '{"query": "Is a prenuptial agreement enforceable in India?"}'
   ```
   *Response: Professional advice noting public policy concerns.*

2. **Turn 2: Contextual Follow-up**
   ```bash
   curl -X POST http://localhost:7860/chat -d '{"query": "How does Section 23 of Contract Act apply to it?", "session_id": "[prev_id]"}'
   ```
   *Response: Explains 'it' (the prenup) in the context of immoral/unlawful considerations.*

3. **Criminal Procedure Inquiry**
   ```bash
   curl -X POST http://localhost:7860/chat -d '{"query": "Can the police arrest without a warrant for a bailable offense?"}'
   ```
   *Response: Cites CrPC limitations and relevant precedents.*

4. **Service Law Scenario**
   ```bash
   curl -X POST http://localhost:7860/chat -d '{"query": "Can a government employee be dismissed without an inquiry?"}'
   ```
   *Response: References Article 311 and the 'Principles of Natural Justice'.*

5. **IPR Rights Query**
   ```bash
   curl -X POST http://localhost:7860/chat -d '{"query": "What is the duration of copyright for a literary work in India?"}'
   ```
   *Response: Provides statutory timelines (Life + 60 years) grounded in Copyright Act.*

---

## 3. IRAC Case Briefing Endpoint (`/brief`)
Deep-dive single-case analyst.

### Specification
- **Method**: `POST`
- **Path**: `/brief/{case_id}`
- **Parameter**: `case_id` (e.g., `case_vishaka_1997`).

### 5 Landmark ID Examples
| Case ID | Context |
| :--- | :--- |
| `case_maneka_1978` | "Right to Life" scope expansion. |
| `case_vishaka_1997` | Workplace sexual harassment guidelines. |
| `case_dkbasu_1997` | Custodial death and arrest protocol. |
| `case_navtej_2018` | Decriminalization of Section 377. |
| `case_shrinath_2023` | Modern electronic evidence admissibility. |

---

## 4. Administrative Endpoints

### List Sessions (`GET /sessions`)

Returns all active conversation threads for administrative monitoring.


```bash
curl http://localhost:7860/sessions
```

---

## 5. Public Access via Ngrok

For remote testing or frontend integration without local deployment, the API can be exposed using ngrok.

### Setup Instructions

1. **Launch API**: Ensure the FastAPI server is running on port 7860.
2. **Start Tunnel**:

```bash
ngrok http 7860
```

1. **Verified Endpoint**: The current active tunnel for the Legal AI RAG system is:
   `https://willy-segmentary-superinnocently.ngrok-free.dev`

> [!TIP]
> When testing via ngrok, the `verify=False` flag may be required in Python `requests` or `--insecure` in `curl` if using the free tier's automated certificates.

---
*Documentation updated after successful port forwarding verification.*
