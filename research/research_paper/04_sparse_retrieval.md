# 4. Sparse Retrieval Methodology

## 4.1 Indexing and Lexical Matching
In our implementation, Sparse Retrieval serves as the baseline for precise keyword matching. We utilize a highly optimized index that approximates the **BM25 (Best Matching 25)** ranking function. BM25 is a probabilistic retrieval model that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity to each other.

### 4.2 Handling Complex Legal Metadata
Sparse retrieval is particularly effective when dealing with structured legal metadata:
- **Case Titles**: Exact titles like "State vs. John Doe".
- **Legal Citations**: Specific references like "2012 AIR SCW 1781".
- **Court Jurisdictions**: Filtering based on specific courts (e.g., Supreme Court of India).

## 4.3 Limitations: The Vocabulary Mismatch
While Sparse Retrieval provides high precision for "Known-Item Search", it suffers from limited recall when the query uses different terminology than the target case. This necessitates the inclusion of dense semantic signals to handle conceptual relevance.

## 4.4 Technical Implementation
- **Data Structure**: Inverted Index mapping tokens to document IDs.
- **Preprocessing**: Removal of boilerplate, normalization of citations, and Porter stemming to reduce word variants.
- **Time Complexity**: $O(n)$ where $n$ is the number of query terms.
