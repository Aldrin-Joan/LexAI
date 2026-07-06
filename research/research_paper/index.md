# Indian Legal Case Discovery: A Multi-Signal Hybrid Retrieval Approach

## Executive Summary
This research presents a robust framework for legal document discovery that bridges the gap between expert citation-based search and layman narrative-style inquiries. By integrating lexical BM25 precision, transformer-based semantic embeddings (MPNet), and structural authority signals (PageRank) via a weighted Reciprocal Rank Fusion (RRF) mechanism, the system achieves state-of-the-art performance for Indian legal corpora.

## 📌 Critical Response to Review
- **[Critique Resolution](critique_resolution.md)**: A point-by-point defense and implementation summary addressing Methodological Critique and Literature Review requirements.

## Modular Research Paper Structure

1.  **[Abstract](01_abstract.md)**: Formal overview of motivation and findings.
2.  **[Introduction](02_introduction.md)**: The lexical gap and citation power law challenges.
3.  **[Related Work](02b_related_work.md)**: Literature review (RRF, LegalBERT, G-DSR).
4.  **[Methodology Overview](03_methodology_overview.md)**: The hybrid retrieval architecture.
5.  **[Sparse Retrieval](04_sparse_retrieval.md)**: BM25 and lexical optimization.
6.  **[Dense Retrieval](05_dense_retrieval.md)**: Semantic latent space and MPNet baselines.
7.  **[Graph Analysis](06_graph_retrieval.md)**: PageRank as structural authority bias.
8.  **[Weighted RRF Fusion](07_weighted_rrf_fusion.md)**: Rank consolidation and dynamic weighting.
9.  **[Experimental Setup](08_experimental_setup.md)**: Metrics, ground truth, and hardware.
10. **[Results and Analysis](09_results_analysis.md)**: Performance evaluation (N=5255 and N=50).
11. **[Conclusion](10_conclusion.md)**: Contributions and future directions.

---
**Author**: Antigravity Research Team
**Date**: March 2026
