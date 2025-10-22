# llmextract

A Python library to extract structured information from unstructured text using LLMs, powered by LangChain. It supports multiple providers like OpenRouter and Ollama out of the box.

## Features

- **Multi-Provider Support**: Seamlessly switch between cloud-based models (via OpenRouter) and local models (via Ollama).
- **Structured Output**: Uses Pydantic and few-shot prompting to ensure reliable, structured JSON output.
- **Source Grounding**: Automatically finds the exact character positions of extractions in the source text.
- **Long Document Support**: Handles documents larger than a model's context window via intelligent chunking.
- **Interactive Visualization**: Generate a self-contained HTML report to review extractions in context.

## Installation

```bash
pip install llmextract
```

## Quick Start

1.  **Set up your API keys.** Create a `.env` file in your project root:

    ```
    # For cloud models via OpenRouter
    OPENROUTER_API_KEY="sk-or-..."

    # For local models, ensure Ollama is running
    # ollama serve
    ```

2.  **Run an extraction.** Create a Python script and add the following:

    ```python
    from dotenv import load_dotenv
    from llmextract import extract, ExampleData, Extraction

    # Load API keys from .env file
    load_dotenv()

    # 1. Define the extraction task with a clear prompt and examples
    prompt = "Extract patient names, medications, and conditions."
    examples = [
        ExampleData(
            text="Jane took 20mg of Zoloft for depression.",
            extractions=[
                Extraction(extraction_class="patient", extraction_text="Jane"),
                Extraction(extraction_class="medication", extraction_text="Zoloft"),
                Extraction(extraction_class="condition", extraction_text="depression"),
            ],
        )
    ]

    # 2. Define the input text
    text = "The patient, John Doe, was prescribed Lisinopril for hypertension."

    # 3. Call the extract function
    result_doc = extract(
        text=text,
        prompt_description=prompt,
        examples=examples,
        model_name="mistralai/mistral-7b-instruct:free", # An OpenRouter model
    )

    # 4. Programmatically access the results
    print("--- Extracted Data ---")
    for extraction in result_doc.extractions:
        print(f"Class: {extraction.extraction_class}, Text: '{extraction.extraction_text}'")
        if extraction.char_interval:
            print(f"  -> Found at characters {extraction.char_interval.start}-{extraction.char_interval.end}")
    ```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
