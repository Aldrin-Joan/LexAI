# 5. Dense Retrieval Methodology

## 5.1 Beyond Keywords: The Latent Space
Unlike traditional keyword search, Dense Retrieval maps every document and query into a high-dimensional latent space. This space captures the deep semantic properties of the text through transformer-based embeddings. In our system, each legal case is represented as a **768-dimensional vector**.

## 5.2 The all-mpnet-base-v2 Model
We chose the `all-mpnet-base-v2` transformer model for its exceptional performance in clustering conceptually similar documents for layman users. 
- **Model Details**: The model is fine-tuned for semantic text similarity (STS) using millions of real-word sentence pairs.
- **Empirical Justification (Ablation)**: While general-purpose SOTA models like MPNet provide robust zero-shot recovery, we conducted an ablation against **`InLegalBERT`** on a stratified sample (N=500 targets) against a **10,000-candidate noise floor**. InLegalBERT achieved **100.0% Recall@10** compared to MPNet's **82.4%**, specifically in a sample that was **100% Supreme Court of India** judgments. This highlights the superior domestic specificity for formal legal nomenclature, justifying its use as a specialized signal for court-specific discovery.

## 5.3 Technical Implementation: FAISS Indexing
Since the legal corpus contains over 700,000 cases, a linear search ("brute force") of the latent space is computationally prohibitive.
- **Index Type**: We utilize **FAISS** (Facebook AI Similarity Search) with an **IndexFlatL2** or **IVF** structure for sub-millisecond retrieval.
- **Similarity Metric**: Measured using $L_2$ Euclidean distance, where a smaller distance denotes higher semantic relevance.

## 5.4 Performance Advantages
- **Robustness to Misspellings**: Vectors are derived from sub-word tokens, making them less sensitive to typos.
- **Concept Discovery**: Identifying cases related to "unlawful termination of employment" even if the query only mentions "firing" or "lost my job".
