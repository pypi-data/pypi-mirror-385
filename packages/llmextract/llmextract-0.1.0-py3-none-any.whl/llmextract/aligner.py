# llmextract/aligner.py

import logging
from typing import List

from .data_models import CharInterval, Extraction

# Configure a logger for this module so users can control output verbosity
logger = logging.getLogger(__name__)


def align_extractions(
    extractions: List[Extraction], original_text: str
) -> List[Extraction]:
    """
    Aligns extracted text with the original source text to find character positions.

    It first attempts to find matches in order. If that fails, it falls back to
    searching from the beginning of the document to handle out-of-order
    LLM responses.

    Args:
        extractions: A list of Extraction objects to be aligned.
        original_text: The source text from which the extractions were made.

    Returns:
        The same list of Extraction objects, with `char_interval` populated where possible.
    """
    last_match_end = 0
    aligned_extractions = []
    lower_original = original_text.lower()

    for extraction in extractions:
        search_text = extraction.extraction_text.lower()

        start_index = lower_original.find(search_text, last_match_end)

        if start_index == -1:
            start_index = lower_original.find(search_text)
            if start_index != -1:
                logger.debug(
                    "Extraction '%s' found out of order. Falling back to full text search.",
                    extraction.extraction_text,
                )

        if start_index != -1:
            end_index = start_index + len(extraction.extraction_text)
            extraction.char_interval = CharInterval(start=start_index, end=end_index)

            if start_index >= last_match_end:
                last_match_end = end_index
        else:
            logger.warning(
                "Could not align extraction: '%s'", extraction.extraction_text
            )

        aligned_extractions.append(extraction)

    return aligned_extractions
