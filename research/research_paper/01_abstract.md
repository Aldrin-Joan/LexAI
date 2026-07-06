# Legal Discovery Optimized: A Multi-Modal Research Paper

## Abstract

In the modern legal landscape, the volume of digital case law is growing exponentially, rendering traditional keyword-based retrieval systems increasingly insufficient. This paper presents a novel multi-modal retrieval framework specifically designed for legal discovery, which integrates three distinct signals: (1) **Lexical Precision** via Sparse Retrieval (BM25 proxy), (2) **Semantic Intent** via transformer-based Dense Retrieval (MPNet), and (3) **Structural Authority** via graph-based network analysis (PageRank).

We demonstrate that while individual retrieval modes capture different facets of relevance, a search engine's robustness is **maximized** through a **Weighted Reciprocal Rank Fusion (RRF)** mechanism. This mechanism dynamically re-weights semantic signals when encountering descriptive, narrative-style queries (e.g., layman problem descriptions). 

Experimental results on a corpus of over 728,000 cases and a large-scale evaluation split of 5,255 cases demonstrate that our proposed weighted hybrid approach achieves significant improvements over pure lexical baselines, achieving a **67.8% Recall@10** on the standardized benchmark. Furthermore, a simulated layman intent benchmark confirms the system's ability to map complex narratives to high-impact legal precedents with 70% accuracy, specifically addressing scenarios where traditional sparse methods fail.
