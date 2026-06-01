# 📊 Performance Metrics & Benchmark Dataset

The results provided in this directory represent the evaluation of the Hybrid Legal RAG system across multiple retrieval modalities.

## 📈 Performance Comparison (Batch N=5255)

The table below summarizes our standardized benchmarks. The **Hybrid (Sparse+Dense+Graph)** mode consistently outperforms single-modality retrievers.

| Modality | Top-1 Accuracy | NDCG@10 | Latency (mean) |
| :--- | :--- | :--- | :--- |
| Sparse (BM25) | 58.2% | 0.65 | 0.1s |
| Dense (InLegalBERT) | 71.4% | 0.78 | 0.4s |
| Dense (MPNet v2) | 76.8% | 0.82 | 0.4s |
| **Hybrid (Fused)** | **82.4%** | **0.89** | **1.1s** |

---

## 🔬 Ablation Studies

### High-Noise Floor Test (N=10,000)
To test the robustness of the **Graph (PageRank)** component, we executed a "Noise Floor Ablation" by injecting 10,000 random non-Supreme Court cases into the search indices.

- **Without Graph**: Accuracy dropped to **65.3%** as sparse/dense embeddings were overwhelmed by semantic noise.
- **With Graph**: Accuracy remained at **81.2%**, as the PageRank weighting correctly prioritized established Supreme Court precedents over random noise.

---

## 🗄️ File Manifest
- `Legal_Case_Search_System_Results_Report.docx`: The comprehensive engineering and research report.
- `experiment_results_tier1.csv`: Raw execution results per query, including precision and recall per retrieval mode.
