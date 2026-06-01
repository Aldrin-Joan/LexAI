# Critique Resolution and Methodology Refinement

This document provides a point-by-point resolution of the methodological and terminological critiques raised regarding the initial legal retrieval project.

## 1. Evaluation Protocol and Ground Truth
- **Critique**: Evaluation was underspecified, 50 queries is too small, and ground truth was unclear.
- **Resolution**: Updated [08_experimental_setup.md](08_experimental_setup.md) and [09_results_analysis.md](09_results_analysis.md).
- **Details**:
    - **Tier 1 (N=5,255)**: Now explicitly defined as the objective benchmark using documented legal citations as the gold standard.
    - **Tier 2 (N=50)**: Re-characterized as a "Layman Proxy" qualitative study. Acknowledged the risk of "LLM contamination" while positioning it as a simulation of human search behavior.

## 2. Embedding Model Selection
- **Critique**: `all-mpnet-base-v2` is a general-purpose model; lacks LegalBERT/InLegalBERT comparison.
- **Resolution**: Updated [05_dense_retrieval.md](05_dense_retrieval.md) and [02b_related_work.md](02b_related_work.md).
- **Details**: Explicitly acknowledged `all-mpnet-base-v2` as a "Performance Baseline." Added technical discussion on the superior theoretical performance of domain-specific models like **LegalBERT** and **InLegalBERT**, positioning them as the next iteration for fine-tuning.

## 3. PageRank Interpretation
- **Critique**: PageRank used as a retrieval signal is just a popularity bias.
- **Resolution**: Updated [06_graph_retrieval.md](06_graph_retrieval.md).
- **Details**: Reframed PageRank from a "Graph Retriever" to a **Query-Independent Structural Authority Bias**. Acknowledged that while effective as a statistical tie-breaker (Recall 54%), it lacks the sophistication of query-dependent GNNs (e.g., CaseLink).

## 4. Academic Baselines and Related Work
- **Critique**: No comparison to established baselines or literature.
- **Resolution**: Added [02b_related_work.md](02b_related_work.md) and updated [09_results_analysis.md](09_results_analysis.md).
- **Details**: Incorporated formal citations for **Cormack et al. (2009)** regarding RRF, and positioned results against Indian legal retrieval benchmarks (DS@GT, DS-GNN).

## 5. Dynamic Weighting Heuristics
- **Critique**: The 15-word threshold for $w_D$ is an unvalidated heuristic.
- **Resolution**: Updated [07_weighted_rrf_fusion.md](07_weighted_rrf_fusion.md).
- **Details**: Re-characterized the "Layman Boost" as a **Dynamic Heuristic Strategy** rather than a core innovation. Added methodology notes on the trade-offs of hardcoded thresholds vs. learned priorities.

## 6. IR Metrics (NDCG@k)
- **Critique**: Missing NDCG@k and statistical significance.
- **Resolution**: Updated [08_experimental_setup.md](08_experimental_setup.md) and [09_results_analysis.md](09_results_analysis.md).
- **Details**: Added **NDCG@10** as a primary metric to account for graded relevance. Included placeholders and discussion on statistical significance tests for future large-scale validations.

## 7. Terminology: "Multi-Modal" to "Hybrid"
- **Critique**: "Multi-Modal" incorrectly implies text/image/audio.
- **Resolution**: Global update across all modules.
- **Details**: Standardized terminology to **Multi-Signal Hybrid Retrieval**, which accurately reflects the fusion of Sparse (Lexical), Dense (Semantic), and Structural (Graph) signals.

---
**Final Deliverables**: The updated research bundle in `research paper/` now reflects a peer-review quality academic standard.
