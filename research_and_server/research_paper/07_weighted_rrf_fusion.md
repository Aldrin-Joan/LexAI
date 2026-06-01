# 7. Weighted Reciprocal Rank Fusion (RRF)

## 7.1 The Rank Consolidation Problem
A fundamental challenge in hybrid retrieval is the aggregation of results from diverse scoring systems. Sparse retrieval produces lexical BM25 scores, Dense retrieval produces $L_2$ Euclidean distances, and Graph retrieval produces query-independent PageRank importance values. Attempting to normalize these values directly is often mathematically unsound and computationally expensive.

## 7.2 The RRF Algorithm
To overcome this, we utilize **Reciprocal Rank Fusion (RRF)**, a consensus-based approach established by **Cormack et al. (2009)**. RRF generates a merged ranking by summing the reciprocal ranks of documents across all candidate lists. For a document $d$ in a set of result lists $R$:
$$RRFscore(d, R) = \sum_{r \in R} \frac{1}{k + rank(d, r)}$$
Where $rank(d, r)$ denotes the rank of $d$ in the $r$-th list, and $k=60$ acts as a hyperparameter to smooth the influence of top-ranked results.

## 7.3 Adapting Weighted RRF
In our framework, we introduce importance-based weights ($w_i$) to allow the system to dynamically prioritize specific signals:
$$FinalScore(d) = \sum_{i \in Models} w_i \cdot RRFscore(d, R_i)$$

This weighted adaptation allows the system to adjust retrieval behavior per query type.

## 7.4 Dynamic Heuristic Strategy
We address the layman-lexical gap by implementing a dynamic weighting policy. When the system detects a "Descriptive Narrative Query" (quantified as query length $> 15$ tokens), it shifts priority toward the semantic (Dense) signal:
- **Baseline Weights ($w_S, w_D, w_G$):** $1.0, 1.2, 0.8$
- **Descriptive Boost:** Set $w_D = 1.8$

This heuristic ensures that the transformer model's conceptual intent matching takes priority over standard keyword lookups in conversational scenarios.
