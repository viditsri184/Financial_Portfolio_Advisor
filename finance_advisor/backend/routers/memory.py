from fastapi import APIRouter, HTTPException
from backend.memory.store import memory_store

router = APIRouter(prefix="/memory", tags=["memory"])

@router.post("/save")
def save_memory(payload: dict):
    try:
        session_id = payload["session_id"]
        data = payload["data"]
        memory_store.save_entity(session_id, data)
        return {"status": "success"}
    except Exception as ex:
        raise HTTPException(500, str(ex))
