# NyayGraph: Deployment & Operations Guide

This guide details the steps required to deploy the Legal RAG system into production environments, including local servers, cloud VPS, and Hugging Face Spaces.

## 1. Environment Configuration

The system relies on a `.env` file for core secrets and service URLs.

| Variable | Required | Description |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY` | **Yes** | Your Gemini API Key from Google AI Studio. |
| `GEMINI_MODEL` | **Yes** | Recommended: `gemini-2.5-flash` or `gemini-2.5-pro`. |
| `UPSTASH_REDIS_REST_URL` | No | Use this for cloud-persistent chat history. |
| `UPSTASH_REDIS_REST_TOKEN`| No | Token for Upstash Redis access. |
| `INDEX_DB_PATH` | No | Path to `index.db` (Default: `data/index.db`). |

---

## 2. Infrastructure Setup

### A. Session Management (Persistence)
- **Local**: By default, sessions are stored as JSON files in the `/sessions` directory.
- **Cloud (Upstash Redis)**: For auto-scaling or serverless deployments, provide the `UPSTASH_REDIS_REST_URL`. The system will automatically switch to Redis for session state.

### B. Retrieval Engine
- **Database**: Ensure `final_submission/data/index.db` is present. It contains metadata and body text for all 26,000+ cases.
- **Vector Index (FAISS)**: The system supports an optional 2.2GB `.faiss` vector file. 
    - If present, it provides semantic search. 
    - If absent, the system **gracefully falls back** to Keyword (BM25) search.

---

## 3. Deployment Scenarios

### Scenario 1: Local / VPS (REST API)
Ideal for integrating with a custom frontend or mobile app.
1. **Requirements**: Python 3.9+, Nginx (Recommended for Proxy).
2. **Setup**:
   ```bash
   pip install -r requirements.txt
   uvicorn code.api:app --host 0.0.0.0 --port 8000 --workers 4
   ```
3. **Nginx Config**: Map `api.yourdomain.com` to port `8000`.

## 3. Production Deployment: Hugging Face + Upstash Redis

This is the recommended configuration for a multi-user production environment. Hugging Face Spaces provides the UI/API hosting, while Upstash Redis ensures that user chat history persists even if the Space restarts or scales.

### Step 1: Redis Connectivity (Session Persistence)
The system supports two production Redis backends. Choose the one that matches your infrastructure:

#### Option A: Upstash Redis (HTTP - Serverless Friendly)
1. Get the **REST URL** and **Token** from [Upstash Console](https://console.upstash.com/).
2. Set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` in your environment.

#### Option B: Redis Cloud / Redis Labs (TCP - Standard)
1. Get your **Endpoint**, **Port**, and **Password** from [Redis Cloud](https://app.redislabs.com/).
2. Set the following variables in your environment:
    - `REDIS_HOST`: (e.g. `redis-123.c12.ap-south-1.ec2.redislabs.com`)
    - `REDIS_PORT`: (e.g. `12345`)
    - `REDIS_USER`: (Default: `default`)
    - `REDIS_PASSWORD`: Your instance password.

### Step 2: Hugging Face Space Configuration
...
1.  Create a new **Streamlit Space**.
2.  Upload the `final_submission/` folder contents to the repository root.
3.  **Critical: Set Secrets**
    Go to `Settings` -> `Variables and secrets` -> `New secret`. Add:
    - `GOOGLE_API_KEY`: Your Gemini Key.
    - `UPSTASH_REDIS_REST_URL`: The URL from Step 1.
    - `UPSTASH_REDIS_REST_TOKEN`: The Token from Step 1.
    - `GEMINI_MODEL`: (e.g., `gemini-1.5-flash`).

### Step 3: Deployment Verification
- Once the Space builds, open the UI. 
- Start a chat. 
- Refresh the page. Because of the Redis integration, your **conversation history will remain intact**.

---

## 4. Local / VPS Deployment (Standalone REST API)
...

### Scenario 3: Dockerized Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "code.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Maintenance Tasks

### Indexing New Cases
If you add new TXT files to `data/full_texts`, run the ingestion utility to update the SQLite database:
```bash
python code/ingest_texts.py
```

### Health Check
Monitor the endpoint status:
`GET http://localhost:8000/` -> Expected: `{"status": "active"}`

---

## 5. Security Recommendations
- **API Lockdown**: If exposing the FastAPI endpoint publicly, add a dependency for `API Key` verification in `code/api.py`.
- **Rate Limiting**: Use `slowapi` or Nginx rate-limiting to prevent excessive LLM costs.
