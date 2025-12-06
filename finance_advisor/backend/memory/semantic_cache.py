import numpy as np
import uuid
from backend.rag.embedder import embed_texts
from backend.db.redis_client import redis_client
from backend.rag.vector_store import vector_store

CACHE_PREFIX = "semantic_cache:"

def normalize(text: str) -> str:
    text = text.lower().strip().replace("\n", " ")
    return " ".join(text.split())

def search_cache(query: str, threshold: float = 0.75):
    query = normalize(query)

    vec = embed_texts([query])[0]
    embedding = np.array(vec, dtype=np.float32)

    scores, ids = vector_store.search_semantic_cache(embedding)

    if len(ids) == 0:
        return None

    best_score = float(scores[0])
    best_id = ids[0]

    if best_score < threshold:
        return None

    print(f"[CACHE] HIT score={best_score:.3f} id={best_id}")

    key = f"{CACHE_PREFIX}{best_id}"
    cached = redis_client.hgetall(key)
    return cached.get("response")


def save_cache(query: str, response: str):
    query = normalize(query)

    vec = embed_texts([query])[0]
    emb = np.array(vec, dtype=np.float32)

    cache_id = str(uuid.uuid4())

    vector_store.add_cache_embedding(cache_id, emb)

    key = f"{CACHE_PREFIX}{cache_id}"
    redis_client.hset(key, "query", str(query))
    redis_client.hset(key, "response", str(response))

    print(f"[CACHE] SAVED id={cache_id}")
    return True
