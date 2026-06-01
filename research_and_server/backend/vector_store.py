"""
Vector Store for Semantic Search (Phase 2: Multi-Vector).

Uses sentence-transformers for embedding generation and FAISS for efficient similarity search.
Implements Chunking aggregation (Max-Sim) to solve context retrieval limits.
"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Tuple, Any
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from config import Config
from storage_manager import StorageManager
from utils import print_info, print_success, print_error


class VectorStore:
    def __init__(self, index_path: str = "data/indices/vector_index.faiss"):
        self.index_path = index_path
        self.mapping_path = index_path + ".map"
        # Upgrade to SOTA model (Project Ultra)
        self.model_name = 'all-mpnet-base-v2'
        self.dimension = 768  # Dimension for all-mpnet-base-v2
        self.index = None
        self.id_map = {}  # int index -> case_id
        self._model = None  # Lazy load

    @property
    def model(self):
        if self._model is None:
            print_info(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            # Use GPU if available
            import torch
            if torch.cuda.is_available():
                self._model = self._model.to('cuda')
                print_info("Model loaded on GPU.")
            else:
                self._model = self._model.to('cpu')
                print_info("Model loaded on CPU.")
        return self._model

    def _init_index(self):
        """Initialize a new FAISS index."""
        self.index = faiss.IndexFlatIP(
            # Inner Product (Cosine sim for normalized vectors)
            self.dimension)
        self.id_map = {}

    def load_index(self) -> bool:
        """Load existing index from disk."""
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            try:
                print_info(f"Loading vector index from {self.index_path}...")
                self.index = faiss.read_index(self.index_path)
                with open(self.mapping_path, 'rb') as f:
                    self.id_map = pickle.load(f)
                print_success(
                    f"Loaded index with {self.index.ntotal} vectors.")
                return True
            except Exception:
                # Silently fail, search engine handles fallback
                return False
        return False

    def save_index(self):
        """Save index to disk."""
        if self.index:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            with open(self.mapping_path, 'wb') as f:
                pickle.dump(self.id_map, f)
            print_success("Vector index saved.")

    def _chunk_text(self, text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= len(text):
                break
            start += chunk_size - overlap
        return chunks

    def build_from_db(self, batch_size: int = 128):
        """Build vector index from all cases in SQLite database (Multi-Vector)."""
        storage = StorageManager()
        import sqlite3
        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()

        # Count total
        cursor.execute("SELECT COUNT(*) FROM cases")
        total = cursor.fetchone()[0]

        print_info(
            f"Building vector index for {total} cases (Multi-Vector)...")
        self._init_index()

        # Fetch data
        cursor.execute(
            "SELECT case_id, title, main_category, sub_category FROM cases")

        batch = []
        ids = []
        count = 0

        # Pre-load Config for path resolution
        full_text_dir = Path(Config.FULL_TEXTS_DIR)

        for row in tqdm(cursor, total=total, desc="Encoding"):
            case_id, title, main_cat, sub_cat = row

            # Read full text file
            case_text = ""
            try:
                file_path = full_text_dir / f"{case_id}.txt"
                if file_path.exists():
                    case_text = file_path.read_text(
                        encoding='utf-8', errors='ignore')
            except Exception:
                pass

            # Context header for every chunk
            header = f"{title}. {main_cat}. {sub_cat}. "

            # If text is empty, just index the header
            if not case_text:
                full_chunk = header
                batch.append(full_chunk)
                ids.append(case_id)
            else:
                # Create chunks
                # MPNet limit is 512 tokens (~2000 chars).
                # We use 1500 chars for body + header.
                text_chunks = self._chunk_text(
                    case_text, chunk_size=1500, overlap=300)

                for chunk in text_chunks:
                    full_chunk = f"{header}{chunk}"
                    batch.append(full_chunk)
                    ids.append(case_id)

            if len(batch) >= batch_size:
                self._add_batch(batch, ids, count)
                count += len(batch)
                batch = []
                ids = []

        if batch:
            self._add_batch(batch, ids, count)

        self.save_index()
        conn.close()

    def _add_batch(self, texts: List[str], case_ids: List[str], start_idx: int):
        """Encode and add a batch of texts."""
        embeddings = self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True)
        self.index.add(embeddings)

        for i, case_id in enumerate(case_ids):
            self.id_map[start_idx + i] = case_id

    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for similar cases (Aggregating chunks).
        Returns: List of (case_id, score)
        """
        if not self.index and not self.load_index():
            print_error("Index not loaded. Build it first.")
            return []

        query_embedding = self.model.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True)

        # Request more candidates to account for multiple chunks per case
        search_k = k * 15  # Heuristic: assume average 10-15 chunks per doc
        D, I = self.index.search(query_embedding, search_k)

        # Aggregate: Max score per case
        case_scores = {}

        for i, idx in enumerate(I[0]):
            if idx == -1:
                continue

            case_id = self.id_map.get(idx)
            if not case_id:
                continue

            score = float(D[0][i])

            # Max pooling
            if case_id in case_scores:
                if score > case_scores[case_id]:
                    case_scores[case_id] = score
            else:
                case_scores[case_id] = score

        # Sort and trim
        sorted_cases = sorted(case_scores.items(),
                              key=lambda x: x[1], reverse=True)
        return sorted_cases[:k]
