# llmextract/data_models.py

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CharInterval(BaseModel):
    """
    Represents the character interval of an extraction in the source text.

    Attributes:
        start: The starting character index (inclusive).
        end: The ending character index (exclusive).
    """

    start: int
    end: int


class Extraction(BaseModel):
    """
    Represents a single piece of structured information extracted from text.

    Attributes:
        extraction_class: The category or type of the extraction (e.g., "medication").
        extraction_text: The exact text snippet extracted from the source document.
        attributes: A dictionary of structured attributes related to the extraction.
        char_interval: The character position of the extraction in the source text.
                       This is optional as it will be populated after alignment.
    """

    extraction_class: str
    extraction_text: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    char_interval: Optional[CharInterval] = None


class ExampleData(BaseModel):
    """
    Represents a few-shot example for guiding the LLM.

    It consists of a sample input text and the desired structured extractions.

    Attributes:
        text: The example source text.
        extractions: A list of the correct extractions from the text.
    """

    text: str
    extractions: List[Extraction]


class AnnotatedDocument(BaseModel):
    """
    Represents the final output: an original document with all its extractions.

    Attributes:
        text: The original, unstructured source text.
        extractions: A list of all extractions found within the text.
        metadata: An optional dictionary to store metadata about the extraction process
                  (e.g., model name, parameters, document ID).
    """

    text: str
    extractions: List[Extraction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
