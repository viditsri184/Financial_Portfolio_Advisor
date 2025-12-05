import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def save_session_memory(session_id: str, key: str, value: dict | str):
    redis_client.hset(session_id, key, json.dumps(value))

def get_session_memory(session_id: str, key: str):
    data = redis_client.hget(session_id, key)
    return json.loads(data) if data else None

def delete_session(session_id: str):
    redis_client.delete(session_id)
