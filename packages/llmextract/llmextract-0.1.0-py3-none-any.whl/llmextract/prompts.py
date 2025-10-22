# llmextract/prompts.py

import json
from typing import List

from .data_models import ExampleData


def format_prompt(
    prompt_description: str, examples: List[ExampleData], text: str
) -> str:
    """Constructs the final prompt string to be sent to the LLM."""
    prompt_parts = [prompt_description, "\n--- EXAMPLES ---"]
    for example in examples:
        extractions_list = [
            ext.model_dump(exclude={"char_interval"}, exclude_none=True)
            for ext in example.extractions
        ]
        example_output_json = json.dumps({"extractions": extractions_list}, indent=2)
        prompt_parts.append(f"Text:\n'''\n{example.text}\n'''")
        prompt_parts.append(f"JSON Output:\n{example_output_json}")
    prompt_parts.extend(
        [
            "\n--- TASK ---",
            f"Text:\n'''\n{text}\n'''",
            "JSON Output:\nRespond with a single, valid JSON object with an 'extractions' key.",
        ]
    )
    return "\n".join(prompt_parts)
