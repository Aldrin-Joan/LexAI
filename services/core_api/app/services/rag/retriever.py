import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer


class Retriever:
    def __init__(self,
                 index_path="data/faiss_index.index",
                 metadata_path="data/faiss_metadata.json"):

        import os

        # Fallback to faiss.index if default is missing
        if not os.path.exists(index_path) and os.path.exists("data/faiss.index"):
            index_path = "data/faiss.index"

        print(f"Loading FAISS index from {index_path}...")
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            print("WARNING: FAISS index file not found. Creating a dummy index.")
            self.index = faiss.IndexFlatIP(768)  # dummy index

        print(f"Loading metadata from {metadata_path}...")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            print("WARNING: Metadata file not found. Initializing empty metadata.")
            self.metadata = []

        print("Loading embedding model...")
        self.model = SentenceTransformer("intfloat/e5-base-v2")

    def search(self, query, top_k=8):
        query_embedding = self.model.encode(
            f"query: {query}",
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        D, I = self.index.search(np.array([query_embedding]), top_k)

        results = [self.metadata[i] for i in I[0] if 0 <= i < len(self.metadata)]
        return results
