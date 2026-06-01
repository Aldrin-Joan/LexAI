# 📄 Academic Research Paper: Hybrid Legal Retrieval

This directory contains the modularized research paper for the **Hybrid Legal Retrieval (Sparse + Dense + Graph)** system. The content is structured for submission to an applied NLP or Legal AI workshop (e.g., NLLP, JURIX, or ASAIL).

## 🗂️ Paper Modules

| Module # | Section | Key Highlights |
| :--- | :--- | :--- |
| `01_abstract.md` | Abstract | Summary of the 24% Top-1 accuracy boost. |
| `03_methodology_overview.md` | Methodology | Description of the RRF-Fusion and Graph integration. |
| `09_results_analysis.md` | Results & Analysis | Detailed performance on N=5,255 baseline. |
| `critique_resolution.md` | Audit Report | Methodology addressal of Supreme Court bias. |

---

## 🔬 Experimental Setup

Our research used the following parameters:
- **Baseline Dataset**: 5,255 Supreme Court of India precedents.
- **Retriever**: MPNet-based vector search + BM25 keyword matching.
- **Benchmarking Tools**: Normalized Discounted Cumulative Gain (NDCG) and MRR.
- **Ablation Study**: Tested on a 10,000-case noise floor to verify "Graph-Importance Correction".

---

## 🚩 Publication Recommendations

Based on the **Critique Resolution**, it is highly recommended to mention:
1.  **Supreme Court Jurisdictional Bias**: Explicitly state that higher accuracy on landmark cases is partly due to the "Identity-Grounded" nature of Supreme Court precedents.
2.  **Tier 2 Capability**: Positions the system as a Tier 2 tool for "Identity-Grounded" legal analysis rather than a Tier 1 global generalizer.
3.  **Future Scope**: Stratified testing across High Courts and District Courts is essential for Global State-of-the-Art (SOTA) claims.

---

## 🛠️ Usage
To compile the full paper, simply read the files in numerical order or use a markdown compiler (e.g., Pandoc) to merge them for PDF export.
