# 9. Results and Performance Analysis

## 9.1 Overview of Retrieval Tiers
Our evaluation framework distinguishes between two fundamental types of legal search queries: structural keyword-based searches (Tier 1) and conceptual narrative-based searches (Tier 2).

## 9.2 Tier 1 Results: Objective Citation Recovery (N=5,255)
Tier 1 evaluation focuses on the system's ability to recover a specific case given its title and primary legal metadata. This represents the system's effectiveness as a "Keyword-to-Precedent" recovery engine at scale.

| Mode | Recall@10 | MRR |
| :--- | :--- | :--- |
| Sparse (Keyword Only) | 64.2% | 0.403 |
| Graph (PageRank Only) | 53.8% | 0.155 |
| **Hybrid (Fused)** | **67.8%** | **0.410** |

### Observations:
- **Baseline Strength**: Sparse retrieval is remarkably effective for keyword-heavy title searches, achieving 64.2% recall across the full 5,255 test set.
- **Structural Value**: Incorporating PageRank (Graph) into the Hybrid mode provided a statistically relevant boost, demonstrating that global document authority is a valuable signal even in keyword-rich environments.

## 9.3 Tier 2: Simulated Layman Intent Benchmark (N=50)
To evaluate the system's ability to bridge the "Vocabulary Mismatch" gap, we conducted a simulated intent experiment. This task utilized **Identity-Grounded** queries where an LLM generated vague narratives from case summaries, and the system was tasked with recovery.

| Retrieval Mode | Recall@10 (Intent Set) | Delta vs. Keyword |
| :--- | :--- | :--- |
| Sparse (BM25 Only) | 48.0% | - |
| **Weighted Hybrid** | **70.0%** | **+22.0%** |

### Table 3: Precedent Discovery Case Studies
| Layman/Narrative Query | Primary Retrieved Precedent | Search Mode Utility |
| :--- | :--- | :--- |
| "Liability of doctors in brain surgery errors" | *Medical Negligence & Duty of Care* | **Dense Win**: BM25 failed on 'brain' specifics. |
| "Illegal sand mining in Protected Forest zones" | *Environmental Impact Assessment Rule* | **Dense Win**: Recovers 'Illegal' intent over 'sand'. |
| "Offshore shell companies for avoiding GST" | *Indirect Tax Corporate Veil* | **Hybrid Win**: Fuses tax terms with shell intent. |
| "Rights of women in ancestral property" | *Hindu Succession (Amendment) Act* | **Dense Win**: Direct semantic mapping. |
| "Compensation for police custody deaths" | *Custodial Torture & State Liability* | **Hybrid Win**: FTS finds 'death' + Dense finds 'torture'. |

## 9.4 Empirical Ablation: Model Specialization
To compare general-purpose SOTA models against domestic architectures, we conducted an ablation study using a stratified subset (N=500 targets) evaluated against a **10,000-candidate noise floor**.

| Model Baseline | Recall@10 (N=10,500) | Observation |
| :--- | :--- | :--- |
| `all-mpnet-base-v2` | 82.4% | Robust general semantic intent. |
| `law-ai/InLegalBERT` | **100.0%** | Absolute recall on SC-specific nomenclatures. |

> [!IMPORTANT]
> **Jurisdictional Specialization**: A jurisdictional audit revealed that the N=500 sample was 100% composed of Supreme Court of India judgments. The 100% recall achieved by InLegalBERT likely reflects intensive specialization to Supreme Court citation patterns and nomenclature rather than general corpus superiority. This suggests that for formal SC/HC recovery, InLegalBERT is the optimal signal, while MPNet remains the primary driver for broader layman intent.

## 9.5 Discussion: Multi-Signal Fusion
Our findings confirm that **Multi-Signal Hybrid Retrieval** (Sparse + Dense + Structural) is more robust than any single mode. The weighted RRF heuristic effectively dynamically shifts priority towards semantic signals for descriptive queries, solving the "Vocabulary Mismatch" problem inherent in legal search.
