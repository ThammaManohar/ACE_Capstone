from functools import lru_cache

from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedder():
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts):
    model = get_embedder()
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()


def embed_query(text):
    return embed_texts([text])[0]
