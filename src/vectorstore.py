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


def upsert_chunks(chunks, collection=None, batch_size: int = 64):
    """chunks: list of {chunk_id, doc_id, text}"""
    collection = collection or get_collection()
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        ids = [c["chunk_id"] for c in batch]
        texts = [c["text"] for c in batch]
        metadatas = [{"doc_id": c["doc_id"]} for c in batch]
        embeddings = embed_texts(texts)
        collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def query_collection(collection, text: str, top_k: int = 4):
    embedding = embed_query(text)
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    hits = []
    if not results["documents"][0]:
        return hits
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "doc_id": meta["doc_id"], "distance": dist})
    return hits


def query(text: str, top_k: int = 4):
    return query_collection(get_collection(), text, top_k=top_k)


def count():
    return get_collection().count()


def new_session_collection():
    """Create an in-memory, per-session collection that never touches disk."""
    client = chromadb.EphemeralClient()
    return client.get_or_create_collection(name="session_doc")


def query_merged(text: str, session_collection=None, top_k: int = 4):
    """Query the base corpus and, if present, a session collection; merge by distance."""
    hits = query_collection(get_collection(), text, top_k=top_k)
    if session_collection is not None and session_collection.count() > 0:
        hits += query_collection(session_collection, text, top_k=top_k)
    hits.sort(key=lambda h: h["distance"])
    return hits[:top_k]
