# llmextract/chunker.py

from typing import Generator, NamedTuple


class TextChunk(NamedTuple):
    """
    Represents a chunk of text and its starting position in the original document.
    """

    text: str
    start_char: int


def chunk_text(
    text: str, chunk_size: int, chunk_overlap: int
) -> Generator[TextChunk, None, None]:
    """
    Splits a long text into smaller, overlapping chunks.
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap.")

    start = 0
    while start < len(text):
        if len(text) - start < (chunk_size * 0.1):
            break

        end = start + chunk_size
        yield TextChunk(text=text[start:end], start_char=start)

        start += chunk_size - chunk_overlap

