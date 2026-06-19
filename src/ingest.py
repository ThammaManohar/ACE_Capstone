import json
from pathlib import Path

from datasets import load_dataset

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DATASET_NAME, DATASET_SPLIT, MAX_DOCS, ROOT_DIR

DOCS_CACHE_PATH = Path(ROOT_DIR) / "data" / "raw" / "docs.json"


def load_documents():
    """Load a subset of the Indian legal dataset as a list of dicts:
    {doc_id, text, reference_summary}
    """
    ds = load_dataset(DATASET_NAME, split=DATASET_SPLIT)
    ds = ds.select(range(min(MAX_DOCS, len(ds))))

    docs = []
    for i, row in enumerate(ds):
        text = (row.get("Text") or "").strip()
        summary = (row.get("Summary") or "").strip()
        if not text:
            continue
        docs.append({"doc_id": f"doc_{i}", "text": text, "reference_summary": summary})
    return docs


def save_docs_cache(docs):
    DOCS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f)


def load_docs_cache():
    if not DOCS_CACHE_PATH.exists():
        return []
    with open(DOCS_CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Simple character-based sliding-window chunker."""
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks


def chunk_documents(docs):
    """Return list of {doc_id, chunk_id, text} for embedding."""
    chunks = []
    for doc in docs:
        for idx, piece in enumerate(chunk_text(doc["text"])):
            chunks.append({
                "doc_id": doc["doc_id"],
                "chunk_id": f"{doc['doc_id']}_chunk_{idx}",
                "text": piece,
            })
    return chunks
