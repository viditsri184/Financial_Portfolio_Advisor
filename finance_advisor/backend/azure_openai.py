# backend/azure_openai.py

from typing import List, Dict, Any, Optional

from openai import AzureOpenAI

from .config import settings
from httpx import Client as HttpxClient

# -------------------------------------------------
# Azure OpenAI Client
# -------------------------------------------------

# force NO proxies and NO auto-detection
http_client = HttpxClient(trust_env=False)

client = AzureOpenAI(
    api_key=settings.azure_openai_api_key,
    azure_endpoint=settings.azure_openai_endpoint,
    api_version="2024-02-01",
    http_client=http_client
)


# -------------------------------------------------
# Chat (GPT) Wrapper
# -------------------------------------------------
def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 800,
    model: Optional[str] = None,
) -> Any:
    """
    Low-level wrapper for Azure Chat Completions.
    Returns the full response object from Azure.
    """
    deployment = model or settings.azure_openai_chat_deployment

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response


def chat_completion_text(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 800,
    model: Optional[str] = None,
) -> str:
    """
    Convenience wrapper: returns only the response text.
    """
    response = chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        model=model,
    )
    # Defensive check
    if not response.choices:
        return ""
    return response.choices[0].message.content or ""


# -------------------------------------------------
# Embeddings Wrapper
# -------------------------------------------------
def create_embeddings(
    texts: List[str],
    model: Optional[str] = None,
) -> List[List[float]]:
    """
    Returns a list of embeddings, one per input text.
    """
    deployment = model or settings.azure_openai_embedding_deployment

    result = client.embeddings.create(
        model=deployment,
        input=texts,
    )

    # Azure returns a list of objects with .embedding field
    return [item.embedding for item in result.data]
