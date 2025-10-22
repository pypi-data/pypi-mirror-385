# llmextract/services.py

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage

from .chunker import chunk_text
from .data_models import AnnotatedDocument, ExampleData, Extraction
from .parsing import parse_and_align_chunk
from .prompts import format_prompt
from .providers import get_llm_provider


def extract(
    text: str,
    prompt_description: str,
    examples: List[ExampleData],
    model_name: str,
    provider_kwargs: Optional[Dict[str, Any]] = None,
    chunk_size: int = 4000,
    chunk_overlap: int = 200,
    max_workers: int = 10,
) -> AnnotatedDocument:
    """Synchronously extracts structured information, handling long documents in parallel."""
    llm = get_llm_provider(model_name, provider_kwargs)
    chunks = list(chunk_text(text, chunk_size, chunk_overlap))

    def _process_chunk(chunk):
        prompt = format_prompt(prompt_description, examples, chunk.text)
        response = llm.invoke([HumanMessage(content=prompt)])
        if not isinstance(response.content, str):
            raise TypeError(f"Expected str content, got {type(response.content)}")
        return parse_and_align_chunk(response.content, chunk)

    all_extractions: List[Extraction] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_process_chunk, chunk) for chunk in chunks]
        for future in futures:
            all_extractions.extend(future.result())

    metadata = {
        "model_name": model_name,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    }
    if provider_kwargs:
        metadata.update(provider_kwargs)

    return AnnotatedDocument(text=text, extractions=all_extractions, metadata=metadata)


async def aextract(
    text: str,
    prompt_description: str,
    examples: List[ExampleData],
    model_name: str,
    provider_kwargs: Optional[Dict[str, Any]] = None,
    chunk_size: int = 4000,
    chunk_overlap: int = 200,
) -> AnnotatedDocument:
    """Asynchronously extracts structured information, handling long documents."""
    llm = get_llm_provider(model_name, provider_kwargs)
    chunks = list(chunk_text(text, chunk_size, chunk_overlap))

    async def _process_chunk_async(chunk):
        prompt = format_prompt(prompt_description, examples, chunk.text)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        if not isinstance(response.content, str):
            raise TypeError(f"Expected str content, got {type(response.content)}")
        return parse_and_align_chunk(response.content, chunk)

    tasks = [_process_chunk_async(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)

    all_extractions = [ext for chunk_result in results for ext in chunk_result]

    metadata = {
        "model_name": model_name,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    }
    if provider_kwargs:
        metadata.update(provider_kwargs)

    return AnnotatedDocument(text=text, extractions=all_extractions, metadata=metadata)
