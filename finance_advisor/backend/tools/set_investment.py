from backend.memory.store import memory_store

def set_investment_preferences(session_id: str,
                               monthly: float,
                               duration: int,
                               lumpsum: float = 0.0,
                               goal: float = 10000000):
    """
    Save investment preferences into Redis.
    """
    memory_store.save_entity(session_id, {
        "investment_type": "sip",
        "monthly_investment": monthly,
        "tenure_years": duration,
        "lumpsum_investment": lumpsum,
        "goal_amount": goal
    })
    
    return {
        "status": "saved",
        "session_id": session_id,
        "monthly": monthly,
        "duration": duration,
        "lumpsum": lumpsum,
        "goal": goal
    }
