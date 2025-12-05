from backend.db.redis_client import save_session_memory, get_session_memory

class MemoryStore:

    def save_entity(self, session_id, data):
        save_session_memory(session_id, "entity", data)

    def get_entity(self, session_id):
        return get_session_memory(session_id, "entity") or {}

    def save_summary(self, session_id, data):
        save_session_memory(session_id, "summary", data)

    def get_summary(self, session_id):
        return get_session_memory(session_id, "summary")

memory_store = MemoryStore()
