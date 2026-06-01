# 6. Graph Analysis: Structural Authority Bias

## 6.1 The Citation Network as a Directed Graph
Legal case law represents a rich, interconnected network. We model this as a citation graph, $G=(V, E)$, where $V$ is the set of legal cases (vertices) and $E$ is the set of citations (directed edges). A directed edge $A \rightarrow B$ indicates that Case A cites Case B as a precedent.

## 6.2 Pre-Calculating Case Authority: The PageRank Algorithm
To determine the intrinsic "importance" or "authority" of a case, we apply the PageRank algorithm over the global citation network.
- **Damping Factor**: Set to 0.85, following the standard literature for structural authority.
- **Convergence**: Iterative calculation until the PageRank distribution stabilizes across the 700k+ nodes.
- **Topographical Meaning**: A high PageRank identifies cases that are "authoritative" because they are cited by many other authoritative cases (e.g., Supreme Court landmark judgments).

## 6.3 PageRank as a Structural Priority Signal
In our hybrid framework, Graph Retrieval is treated as a **query-independent structural priority bias**. 
- **The "Landmark Boost"**: PageRank is used to prioritize results that have proven to be significant within the legal hierarchy, providing a non-textual quality signal.
- **Noise Reduction**: Helps to mitigate the influence of minor trial court cases that may have high lexical overlap but low legal precedential value.

## 6.4 Limitations and State-of-the-Art
While PageRank provides a robust measure of global authority, it is fundamentally query-independent. Current state-of-the-art research (G-DSR, CaseLink) utilizes **Graph Neural Networks (GNNs)** to learn query-dependent representations through neighbor aggregation. This study utilizes PageRank as a computational baseline for structural authority, providing a path toward more sophisticated graph-text integration in future iterations.

## 6.5 Implementation
- **Storage**: SQLite with a dedicated `pagerank` column.
- **Indexing**: A B-Tree index on `(pagerank, sub_category)` ensures efficient retrieval of authoritative cases within a specific legal domain.
