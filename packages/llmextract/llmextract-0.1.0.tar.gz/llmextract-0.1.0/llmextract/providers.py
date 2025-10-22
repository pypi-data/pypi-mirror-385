# llmextract/providers.py

import os
from typing import Any, Dict, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pydantic import SecretStr


def get_llm_provider(
    model_name: str, provider_kwargs: Optional[Dict[str, Any]] = None
) -> BaseChatModel:
    """Factory to get a LangChain chat model instance."""
    kwargs = provider_kwargs or {}
    is_openrouter_model = "/" in model_name

    if is_openrouter_model:
        api_key = kwargs.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found.")
        return ChatOpenAI(
            model=model_name,
            api_key=SecretStr(api_key),
            base_url=kwargs.get("base_url", "https://openrouter.ai/api/v1"),
            default_headers={
                "HTTP-Referer": os.getenv("YOUR_SITE_URL", ""),
                "X-Title": os.getenv("YOUR_SITE_NAME", ""),
            },
            temperature=0.0,
        )
    else:
        return ChatOllama(
            model=model_name,
            base_url=kwargs.get("ollama_base_url", "http://localhost:11434"),
            temperature=0.0,
        )
