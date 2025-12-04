# backend/routers/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..memory.store import memory_store
from ..azure_openai import chat_completion_text
from ..models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """
    Main conversational endpoint.
    Injects entity memory + summary memory into GPT context.
    """
    try:
        session_id = payload.session_id

        # -------------------------------
        # Fetch memory for current user
        # -------------------------------
        entity_memory = memory_store.get_entity(session_id)
        summary_memory = memory_store.get_summary(session_id)

        # -------------------------------
        # System context for GPT
        # -------------------------------
        system_prompt = (
            "You are a qualified Indian financial advisor. "
            "Provide safe, compliant, SEBI-friendly financial explanations. "
            "Use the memory provided to stay consistent in your recommendations. "
            "Avoid giving guaranteed returns."
        )

        memory_context = (
            f"Entity Memory: {entity_memory}\n"
            f"Summary Memory: {summary_memory or 'None'}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": memory_context},
            {"role": "user", "content": payload.message},
        ]

        # -------------------------------
        # GPT Response
        # -------------------------------
        reply_text = chat_completion_text(messages)

        # For now: no structured tool-calls.
        # In v2 we will enrich this with portfolio_agent, rag_agent, etc.
        return ChatResponse(
            reply=reply_text,
            used_tools=[],
            memory_updates={}
        )

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
