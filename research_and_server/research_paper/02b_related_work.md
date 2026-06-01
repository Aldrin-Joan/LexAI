# 2b. Related Work

## 2b.1 Hybrid Retrieval and Rank Fusion
The integration of lexical and semantic signals has a long history in Information Retrieval (IR). Foundational work by **Cormack et al. (2009)** introduced Reciprocal Rank Fusion (RRF) as an effective, unsupervised way to combine disparate ranked lists. More recent advancements such as **SPLADE** (Formal et al., 2021) and **COIL** (Gao et al., 2021) have pushed the frontier of learned sparse representations, though RRF remains a robust baseline for production environments.

## 2b.2 Legal Domain-Specific Retrievers
Generic embedding models often fail to capture the nuances of legal language. Research has shown that domain-pretrained models like **LegalBERT** (Chalkidis et al., 2020) and **InLegalBERT** (specifically for Indian statutes) significantly outperform general-purpose models like **all-mpnet-base-v2**. This research positions the use of general models as a necessary baseline while acknowledging the superior performance of domain-specialized alternatives.

## 2b.3 Graph-Augmented Legal Search
Structural signals from citation networks have been identified as critical for case similarity. While early approaches used **PageRank** as a static authority signal, state-of-the-art methods like **CaseLink** and **CaseGNN** (arXiv, 2023) utilize Graph Neural Networks (GNNs) to learn joint text-structural representations. **G-DSR** (ACL 2023) and the **NyayGraph (2025)** project further integrate legislative graphs with Large Language Models (LLMs) to identify applicable statutes, representing the current frontier in graph-augmented Indian legal discovery.

## 2b.4 Indian Legal Context
The work of **Bhattacharya et al. (2022)** specifically addresses the Indian judiciary by combining textual and network information, often validated against expert-labeled ground truth. Our work builds on these structural concepts while aligning with recent benchmarks from the **COLIEE 2024** competition, which highlighted the continuing efficacy of hybrid pipelines in legal information retrieval.
