import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

CHUNKS_PATH = "../data/processed/chunks_sample.json"
INDEX_PATH = "../data/faiss_index.index"
METADATA_PATH = "../data/faiss_metadata.json"

print("Loading chunks...")

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 🔥 IMPORTANT: e5 passage prefix
texts = [f"passage: {chunk['text']}" for chunk in chunks]

print(f"Total chunks: {len(texts)}")

print("Loading embedding model on GPU...")
model = SentenceTransformer("intfloat/e5-base-v2", device="cuda")

print("Generating embeddings with normalization...")
embeddings = model.encode(
    texts,
    batch_size=128,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

dimension = embeddings.shape[1]

print("Building FAISS cosine similarity index...")
index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine

index.add(embeddings)

faiss.write_index(index, INDEX_PATH)

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False)

print("Index rebuilt successfully with cosine similarity!")
