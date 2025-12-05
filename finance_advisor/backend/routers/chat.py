# backend/routers/chat.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json

from backend.azure_openai import client
from backend.config import settings
from backend.memory.store import memory_store
from backend.models.chat import ChatRequest, ChatResponse

# Our custom MCP-like tool server
from backend.mcp.server import get_mcp_schema, call_mcp_tool
from backend.guardrails.input_guard import check_user_input
from backend.guardrails.output_guard import sanitize_output, append_disclaimer



router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """
    PURE MCP mode:
    - No manual intent detection
    - No agents
    - Azure GPT sees all tools and decides which one to call
    - Tools executed by our MCP tool registry
    """

    try:
        session_id = payload.session_id

        # -----------------------------
        # 0. Input guardrails
        # -----------------------------
        allowed, guard_msg = check_user_input(payload.message)
        if not allowed:
            return ChatResponse(reply=guard_msg)

        # -----------------------------
        # Load memory
        # -----------------------------
        entity = memory_store.get_entity(session_id)
        summary = memory_store.get_summary(session_id)

        system_prompt = (
            "You are a qualified Indian financial advisor. "
            "You MUST use the provided tools to answer user queries. "
            "If any tool is relevant, NEVER answer directly. "
            "You MUST call a tool instead of responding in natural language. "
            "Only avoid tool calling if absolutely no tool is relevant."
            "IMPORTANT: If a function/tool matches the user request, you MUST call it. "
            "DO NOT answer directly. "
            "Never hallucinate regulatory information — instead call rag_tool. "
            "Never guarantee returns. "
            "Always ensure safety, SEBI compliance, and clarity."
             "You are a SEBI-aware Indian financial advisor assistant. "
            "You MUST follow these rules strictly:\n"
            "1. Do NOT provide guaranteed, risk-free, or sure-shot returns.\n"
            "2. Do NOT suggest illegal, unethical, or non-compliant practices "
            "(including insider trading, market manipulation, tax evasion, or misuse of financial products).\n"
            "3.For product-definitions or financial terms first try calling investment_dict tool if not found there then go to rag_tool"
            "4. For regulatory, SEBI, or product-definition questions or debt, equity, hybrid fund questions,, prefer calling the 'rag_tool' "
            "to retrieve authoritative content, then summarise it.\n"
            "5. Use the tools (risk_profile_tool, portfolio_tool, simulate_tool, currency_tool, nav_tool, rag_tool) "
            "whenever they can improve accuracy or safety.\n"
            "6. Make risk disclosures explicit and remind the user that all market-linked products carry risk.\n"
            "7. If a user asks for something unsafe, illegal, or outside allowed scope, politely refuse and explain why.\n"
        )

        memory_context = (
            f"User Profile Memory: {entity}\n"
            f"Summary Memory: {summary or 'None'}"
        )

        # -----------------------------
        # Build LLM messages
        # -----------------------------
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": memory_context},
            {"role": "user", "content": payload.message},
        ]

        # -----------------------------
        # Step 1: Ask Azure GPT with tools
        # -----------------------------
        response = client.chat.completions.create(
            model=settings.azure_openai_chat_deployment,
            messages=messages,
            tools=get_mcp_schema(),   # <-- Important: our tool schema
            tool_choice="auto"        # <-- GPT chooses when to call tools
        )

        msg = response.choices[0].message

        # -----------------------------
        # Step 2: If GPT calls tools
        # -----------------------------
         # -----------------------------
        # Step 2: If GPT calls tools
        # -----------------------------
        if msg.tool_calls:
            followup_messages = [*messages, msg]

            for tool_call in msg.tool_calls:
                tool_result = call_mcp_tool(tool_call)
                followup_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            print("\n======= GPT REQUESTED TOOL CALL(S) =======")
            for tc in msg.tool_calls:
                print(f"Tool: {tc.function.name}")
                print(f"Arguments RAW: {tc.function.arguments}")
            print("==========================================\n")

            final = client.chat.completions.create(
                model=settings.azure_openai_chat_deployment,
                messages=followup_messages
            )

        # --------------------------------------
        # Extract raw GPT reply (tool or no tool)
        # --------------------------------------
        if msg.tool_calls:
            raw_reply = final.choices[0].message.content
        else:
            raw_reply = msg.content

        raw_reply = raw_reply or ""

        # --------------------------------------
        # Apply output guardrails
        # --------------------------------------
        cleaned_text, _ = sanitize_output(raw_reply)
        final_reply = append_disclaimer(cleaned_text)

        return ChatResponse(reply=final_reply)

    except Exception as ex:
        print("----------- BACKEND /chat ERROR -----------")
        import traceback
        traceback.print_exc()
        print("--------------------------------------------")
        raise HTTPException(status_code=500, detail=str(ex))
