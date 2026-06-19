"""One-time index build: download dataset subset, chunk, embed, persist to Chroma."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingest import chunk_documents, load_documents, save_docs_cache
from src.vectorstore import count, upsert_chunks


def main():
    print("Loading documents from ninadn/indian-legal ...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")

    save_docs_cache(docs)
    print(f"Cached raw documents to data/raw/docs.json")

    print("Chunking documents ...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    print("Embedding and upserting into Chroma (this may take a few minutes) ...")
    upsert_chunks(chunks)

    print(f"Done. Vector store now has {count()} chunks indexed.")


if __name__ == "__main__":
    main()
