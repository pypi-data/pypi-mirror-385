# llmextract/parsing.py

import json
import re
from typing import Any, Dict, List

from .aligner import align_extractions
from .chunker import TextChunk
from .data_models import Extraction


def transform_llm_extractions(
    raw_extractions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Transforms common LLM structural deviations into the valid Extraction format."""
    corrected = []
    for item in raw_extractions:
        if "extraction_class" in item and "extraction_text" in item:
            corrected.append(item)
        elif len(item) == 1:
            key, value = next(iter(item.items()))
            corrected.append(
                {
                    "extraction_class": key,
                    "extraction_text": str(value),
                    "attributes": {},
                }
            )
    return corrected


def parse_and_align_chunk(
    llm_output_content: str, chunk: TextChunk
) -> List[Extraction]:
    """Parses LLM output for a single chunk and aligns its extractions."""
    match = re.search(r"\{.*\}", llm_output_content, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
        raw_extractions = data.get("extractions", [])
        if not isinstance(raw_extractions, list):
            return []

        transformed_dicts = transform_llm_extractions(raw_extractions)
        validated_extractions = [Extraction(**item) for item in transformed_dicts]

        # Align extractions relative to the chunk's local text
        aligned_in_chunk = align_extractions(validated_extractions, chunk.text)

        # Offset the char_interval to be relative to the full original document
        for ext in aligned_in_chunk:
            if ext.char_interval:
                ext.char_interval.start += chunk.start_char
                ext.char_interval.end += chunk.start_char
        return aligned_in_chunk
    except (json.JSONDecodeError, TypeError):
        return []
