# backend/routers/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..memory.store import memory_store
from ..azure_openai import chat_completion_text
from ..models.chat import ChatRequest, ChatResponse
from ..agents.classifier_agent import classifier_agent
from ..agents.portfolio_agent import portfolio_agent
from ..agents.simulation_agent import simulation_agent
from ..agents.rag_agent import rag_agent
from ..agents.intake_agent import intake_agent
from ..agents.advisory_agent import advisory_agent

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

        intent = classifier_agent.classify(user_message=payload.message)
        # Missing info
        if intent == "missing_info":
            follow_up = intake_agent.ask_for_missing_info(payload.session_id, payload.message)
            return ChatResponse(reply=follow_up)

        # SEBI rules / MF definitions
        if intent == "get_sebi_rule":
            ctx = rag_agent.lookup(payload.message, top_k=3)
            injected_context = "\n\n".join([c["text"] for c in ctx])
            final = chat_completion_text([
                {"role": "system", "content": "Answer using provided SEBI rules."},
                {"role": "system", "content": injected_context},
                {"role": "user", "content": payload.message}
            ])
            return ChatResponse(reply=final)

        # Build portfolio
        if intent == "build_portfolio":
            # Load entity memory FIRST
            entity = memory_store.get_entity(payload.session_id)

            required_fields = ["age", "risk_category", "tenure_years"]

            # Check if all required fields exist
            if not all(f in entity for f in required_fields):
                missing = [f for f in required_fields if f not in entity]
                return ChatResponse(
                    reply=f"Before I can build your portfolio, I need the following information: {', '.join(missing)}."
                )

            # Proceed only if required fields exist
            result = portfolio_agent.construct_portfolio(payload.session_id)
            return ChatResponse(reply=result["explanation"])
        
        # Run simulation
        if intent == "run_simulation":
            sim = simulation_agent.run_simulation(payload.session_id)
            return ChatResponse(reply=str(sim))

        # Final advisory plan
        if intent == "final_advice":
            summary = advisory_agent.generate_advice(payload.session_id)
            return ChatResponse(reply=summary)

        # Default: normal LLM chat
        reply = chat_completion_text(messages)
        return ChatResponse(reply=reply)

    except Exception as ex:
        print("----------- BACKEND /chat ERROR -----------")
        import traceback
        traceback.print_exc()
        print("--------------------------------------------")
        raise HTTPException(status_code=500, detail=str(ex))

