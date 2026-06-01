# 2. Introduction: The Challenges of Legal Discovery

## 2.1 The Lexical Gap in Legal Language
Traditional retrieval systems operate primarily on lexical matching—finding documents that contain the exact same words as the query. In the legal domain, this is problematic for several reasons:
- **Synonymy**: Legal concepts can be described using different terms (e.g., "custody" vs. "guardianship" or "alimony" vs. "spousal support").
- **Polysemy**: The same word can have vastly different legal meanings depending on context (e.g., "consideration" in contract law vs. its everyday meaning).
- **Layman Language**: A regular person (layman) describing a legal problem will use natural, descriptive language that rarely overlaps with the formal, archaic phrasing found in judicial opinions.

## 2.2 The Citation Power Law
Legal systems are built on precedent (stare decisis). Judicial opinions frequently cite earlier cases to provide authority for their reasoning. In most legal corpuses, citation frequency follows a power law distribution: a few "landmark" cases are cited thousands of times, while the vast majority are cited sparingly. Identifying these authoritative "hubs" is crucial for high-quality retrieval, but keyword search alone ignore this structural data.

## 2.3 Objectives of this Research
This research aims to bridge these gaps by:
1. Developing a **multi-modal architecture** that treats Sparse, Dense, and Graph signals as complementary.
2. Implementing a **dynamic weighting agent** for Reciprocal Rank Fusion that adjusts retrieval strategies in real-time based on query length and complexity.
3. Conducting a **systematic evaluation** across both standard citation-recovery tasks and complex natural language problem scenarios.
