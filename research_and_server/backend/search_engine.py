"""
Search Engine for Legal Case Knowledge Graph System.

This module implements the hybrid recommendation logic:
1. Query Analysis (LLM)
2. Full-Text Search (SQLite FTS)
3. Scoring & Ranking
"""

import sqlite3
from typing import List, Dict, Any, Optional
from storage_manager import StorageManager
from llm_client import LLMClient
from utils import print_info, print_warning


from enum import Enum


class SearchMode(Enum):
    KEYWORD_ONLY = "keyword"      # Pure Sparse (TF-IDF/BM25)
    SEMANTIC_ONLY = "semantic"    # Pure Dense (Embeddings)
    GRAPH_ONLY = "graph"          # Popularity/Centrality
    HYBRID = "hybrid"             # Sparse + Dense (RRF)
    ULTRA = "ultra"               # Hybrid + Cross-Encoder Re-ranking


class SearchEngine:
    """Hybrid recommendation engine for legal cases."""

    def __init__(self):
        """Initialize search engine."""
        self.storage = StorageManager()
        self.llm = LLMClient()
        # Lazy load vector store and re-ranker
        self._vector_store = None
        self._re_ranker = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            from vector_store import VectorStore
            self._vector_store = VectorStore()
        return self._vector_store

    @property
    def re_ranker(self):
        if self._re_ranker is None:
            from re_ranker import ReRanker
            self._re_ranker = ReRanker()
        return self._re_ranker

    def search(
        self,
        query: str,
        limit: int = 10,
        mode: SearchMode = SearchMode.HYBRID,
        use_llm: bool = True,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant cases using specified mode.
        """
        print_info(f"Searching for: '{query}' (Mode: {mode.value})")

        # 1. Analyze Query
        params = {}
        if use_llm:
            analysis = self.llm.analyze_search_query(query)
            if analysis:
                params = analysis
                print_info(f"Query Analysis: {params}")

        # Extract keywords and filters
        keywords = params.get('keywords', query.split())
        main_cat = main_category if main_category else params.get(
            'main_category')
        sub_cat = sub_category if sub_category else params.get('sub_category')

        # 2. Retrieval Strategy
        candidates = {}  # Map case_id -> score

        if mode == SearchMode.KEYWORD_ONLY:
            candidates = self._sparse_retrieval(query, keywords, limit * 2)

        elif mode == SearchMode.SEMANTIC_ONLY:
            candidates = self._dense_retrieval(query, limit * 2)

        elif mode == SearchMode.GRAPH_ONLY:
            # Graph retrieval logic (simplified for now)
            candidates = self._graph_retrieval(limit * 2, main_cat, sub_cat)

        elif mode in [SearchMode.HYBRID, SearchMode.ULTRA]:
            # RRF Fusion (Use larger pool for re-ranking)
            pool_size = limit * 10 if mode == SearchMode.ULTRA else limit * 5

            sparse_results = self._sparse_retrieval(query, keywords, pool_size)
            
            # DENSE Fallback: Skip if index missing
            try:
                dense_results = self._dense_retrieval(query, pool_size)
            except Exception as e:
                print_warning(f"Dense retrieval skipped: {e}")
                dense_results = {}

            # GRAPH Fallback: Skip if pagerank missing
            try:
                graph_results = self._graph_retrieval(pool_size, main_cat, sub_cat)
            except Exception as e:
                print_warning(f"Graph retrieval skipped: {e}")
                graph_results = {}

            # Combine using Weighted Reciprocal Rank Fusion
            # If only sparse results exist, RRF will still work but only use one list
            result_lists = [sparse_results]
            weights = [1.0]
            
            if dense_results:
                result_lists.append(dense_results)
                weights.append(1.2)
            if graph_results:
                result_lists.append(graph_results)
                weights.append(0.8)

            candidates = self._reciprocal_rank_fusion(
                result_lists,
                k=60,
                weights=weights
            )

        # 3. Post-Processing & Filtering
        final_results = []

        # Hydrate candidate details from DB
        if candidates:
            # Efficient bulk fetch
            candidate_ids = list(candidates.keys())
            conn = sqlite3.connect(self.storage.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            placeholders = ','.join(['?'] * len(candidate_ids))
            # Include full_text in the selection
            cursor.execute(
                f"SELECT * FROM cases WHERE case_id IN ({placeholders})",
                candidate_ids)
            rows = cursor.fetchall()

            case_map = {row['case_id']: dict(row) for row in rows}
            conn.close()

            for cid, score in candidates.items():
                if cid in case_map:
                    case = case_map[cid]
                    case['score'] = round(score, 4)
                    
                    # Store text content from DB (for RAG context and Ultra re-ranking)
                    # We take the first 3000 chars for context to keep it lean
                    case['text_content'] = (case.get('full_text') or '')[:3000]
                    
                    final_results.append(case)

        # 4. Re-ranking (ULTRA Mode)
        if mode == SearchMode.ULTRA:
            print_info("Re-ranking top 100 candidates...")
            # Take top 100 from RRF to capture 85% recall ceiling
            # (vs 70% at @50)
            final_results.sort(key=lambda x: x['score'], reverse=True)
            top_candidates = final_results[:100]

            # Apply Cross-Encoder
            final_results = self.re_ranker.rerank(
                query, top_candidates, top_k=limit)
        else:
            # Standard Sort
            final_results.sort(key=lambda x: x['score'], reverse=True)
            final_results = final_results[:limit]

        return final_results

    def _sparse_retrieval(
        self,
        query: str,
        keywords: List[str],
        limit: int
    ) -> Dict[str, float]:
        """BM25/TF-IDF Retrieval via StorageManager/SQLite FTS."""
        search_term = " OR ".join(
            [f'"{k}"' for k in keywords]) if keywords else query
        results = self.storage.search_cases(search_term, limit=limit)
        # Results from storage.search_cases are ordered by FTS rank
        # We return a dict where the order is preserved for RRF
        return {r['case_id']: 0.0 for r in results}

    def _dense_retrieval(
        self,
        query: str,
        limit: int,
        hyde_document: str = None
    ) -> Dict[str, float]:
        """Vector Search."""
        search_text = hyde_document if hyde_document else query
        vector_results = self.vector_store.search(search_text, k=limit)
        # vector_results is (case_id, distance_score)
        return {cid: score for cid, score in vector_results}

    def _graph_retrieval(
        self,
        limit: int,
        main_cat: str = None,
        sub_cat: str = None
    ) -> Dict[str, float]:
        """Graph/PageRank Retrieval."""
        import sqlite3
        conn = sqlite3.connect(self.storage.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT case_id, pagerank FROM cases"
        params = []
        where_clauses = ["pagerank > 0"]

        if main_cat:
            where_clauses.append("main_category = ?")
            params.append(main_cat)
        if sub_cat:
            where_clauses.append("sub_category = ?")
            params.append(sub_cat)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY pagerank DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return {row['case_id']: row['pagerank'] for row in rows}

    def _reciprocal_rank_fusion(
        self,
        result_lists: List[Dict[str, float]],
        k: int = 60,
        weights: List[float] = None
    ) -> Dict[str, float]:
        """
        Combine multiple ranked lists using Weighted RRF.
        Score = sum(weight_i * (1 / (k + rank_i)))
        """
        final_scores = {}

        if weights is None:
            weights = [1.0] * len(result_lists)

        for i, r_list in enumerate(result_lists):
            weight = weights[i]
            # Convert dict keys to ranked list
            current_ranked_ids = list(r_list.keys())

            for rank, cid in enumerate(current_ranked_ids):
                if cid not in final_scores:
                    final_scores[cid] = 0.0
                # Weighted RRF Formula
                final_scores[cid] += weight * (1 / (k + rank + 1))

        return final_scores
