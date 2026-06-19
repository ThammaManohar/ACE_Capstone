from functools import lru_cache

import chromadb

from src.config import CHROMA_DIR, COLLECTION_NAME
from src.embeddings import embed_query, embed_texts


@lru_cache(maxsize=1)
def get_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def upsert_chunks(chunks, batch_size: int = 64):
    """chunks: list of {chunk_id, doc_id, text}"""
    collection = get_collection()
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        ids = [c["chunk_id"] for c in batch]
        texts = [c["text"] for c in batch]
        metadatas = [{"doc_id": c["doc_id"]} for c in batch]
        embeddings = embed_texts(texts)
        collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def query(text: str, top_k: int = 4):
    collection = get_collection()
    embedding = embed_query(text)
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "doc_id": meta["doc_id"], "distance": dist})
    return hits


def count():
    return get_collection().count()
