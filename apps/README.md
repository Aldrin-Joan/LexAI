# Frontends & Client Applications 🖥️

This directory hosts user-facing applications of the LegalTech monorepo.

---

## 🏛️ Client Communication Flow

```mermaid
graph TD
    User([User]) --> apps/mobile_app & apps/web_app
    
    subgraph Clients [Client Workspaces]
        apps/mobile_app[mobile_app <br> Flutter Multi-platform]
        apps/web_app[web_app <br> React/Vite Playgrounds]
    end

    subgraph Service [Service Backend]
        services/core_api[core_api <br> FastAPI Server]
    end

    apps/mobile_app -->|REST & WebSockets| services/core_api
    apps/web_app -->|REST API Requests| services/core_api
```

---

## 📂 Subprojects

* **[`/mobile_app`](./mobile_app)**: The production Flutter mobile client codebase supporting localized languages, riverpod state providers, and real-time support channels.
* **[`/web_app`](./web_app)**: The production React/Vite web application workspace integrated with Firebase Auth, Firestore client profiling, and live Cloud Run RAG backend querying.
