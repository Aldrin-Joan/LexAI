import json
import os
from tqdm import tqdm

INPUT_PATH = "../data/processed/documents_sample.json"
OUTPUT_PATH = "../data/processed/chunks_sample.json"

CHUNK_SIZE = 1200   # characters
CHUNK_OVERLAP = 200


def clean_text(text):
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue
        if line.isdigit():
            continue
        cleaned.append(line)

    return "\n".join(cleaned)


def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    all_chunks = []

    for doc in tqdm(documents):
        cleaned = clean_text(doc["text"])
        chunks = chunk_text(cleaned)

        for idx, chunk in enumerate(chunks):
            if len(chunk) > 500:
                all_chunks.append({
                    "year": doc["year"],
                    "source_file": doc["file"],
                    "chunk_id": idx,
                    "text": chunk
                })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nTotal chunks created: {len(all_chunks)}")


if __name__ == "__main__":
    main()
