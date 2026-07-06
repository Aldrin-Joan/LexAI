# LegalTech AI Research 🔬

This directory houses the academic, benchmark, and design research behind the Hybrid Legal RAG system.

---

## 🏛️ Research & Evaluation Flow

```mermaid
graph TD
    Data[26,274 Judgments SQLite DB] --> Ingestion[Case Ingest & Index Ingestion]
    Ingestion --> HybridRetrieval[Search Modality Evaluation]
    
    subgraph Modalities [Evaluated Search Modalities]
        Sparse[Sparse BM25]
        Dense[Dense Embeddings]
        Graph[PageRank Weighting]
    end

    HybridRetrieval --> Sparse & Dense & Graph
    Sparse & Dense & Graph --> RRF[Reciprocal Rank Fusion Engine]
    
    RRF --> Evaluation[NDCG & Recall Evaluation]
    Evaluation --> Benchmarks[research/benchmarks]
    Evaluation --> Publications[research/research_paper]
```

---

## 📂 Research Directories

* **[`/benchmarks`](./benchmarks)**: Contains evaluation runs, metric scores, and latency statistics for all search configurations.
* **[`/research_paper`](./research_paper)**: LaTeX and markdown section drafts prepared for Legal AI workshop publications.
* **[`/docs`](./docs)**: Technical reviews, design critiquing, and result analysis reports.
* **[`/wireframes`](./wireframes)**: Design layouts and HTML wireframe mockups for the legal assistant interface.
