# backend/memory/store.py

from typing import Dict, Any
from threading import Lock


class MemoryStore:
    """
    Thread-safe in-memory store.
    Use this for development.
    Replace with Redis or DB in production.
    """

    def __init__(self):
        # session_id -> { "entity": {...}, "summary": "..." }
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    # ------------------------------------------
    # Session Access
    # ------------------------------------------
    def get_session(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._store.setdefault(session_id, {"entity": {}, "summary": ""})

    # ------------------------------------------
    # Update Entity Memory
    # ------------------------------------------
    def update_entity(self, session_id: str, updates: Dict[str, Any]):
        """
        Updates entity memory with dictionary of new values.
        """
        with self._lock:
            session = self._store.setdefault(session_id, {"entity": {}, "summary": ""})
            session["entity"].update(updates)

    # ------------------------------------------
    # Update Summary Memory
    # ------------------------------------------
    def update_summary(self, session_id: str, new_summary: str):
        """
        Replaces summary memory with new summary.
        Typically produced by GPT summarizer.
        """
        with self._lock:
            session = self._store.setdefault(session_id, {"entity": {}, "summary": ""})
            session["summary"] = new_summary

    # ------------------------------------------
    # Fetch Entity Only
    # ------------------------------------------
    def get_entity(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._store.setdefault(session_id, {"entity": {}, "summary": ""})["entity"]

    # ------------------------------------------
    # Fetch Summary Only
    # ------------------------------------------
    def get_summary(self, session_id: str) -> str:
        with self._lock:
            return self._store.setdefault(session_id, {"entity": {}, "summary": ""})["summary"]


# Export global singleton
memory_store = MemoryStore()
