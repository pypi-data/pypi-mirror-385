# llmextract/visualization.py

import json
import textwrap
from typing import List, Union, Dict, Any

from .data_models import AnnotatedDocument, Extraction


_PALETTE: List[str] = [
    "#D2E3FC",
    "#C8E6C9",
    "#FEF0C3",
    "#F9DEDC",
    "#FFDDBE",
    "#EADDFF",
    "#C4E9E4",
    "#FCE4EC",
    "#E8EAED",
    "#DDE8E8",
]

_HTML_TEMPLATE = textwrap.dedent("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>llmextract Visualization</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 20px; background-color: #f9f9f9; }}
        .container {{ max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }}
        .header h2 {{ margin: 0; }}
        .selectors {{ display: flex; gap: 20px; align-items: center; }}
        .selector-container label {{ margin-right: 10px; font-size: 14px; color: #555; }}
        .selector {{ font-size: 14px; padding: 5px; border-radius: 4px; border: 1px solid #ccc; }}
        .metadata-panel {{ font-size: 12px; color: #666; background: #fafafa; padding: 10px; border-radius: 4px; border: 1px solid #eee; margin-bottom: 20px; }}
        .metadata-panel code {{ background: #eee; padding: 2px 4px; border-radius: 3px; }}
        .text-display {{ white-space: pre-wrap; word-wrap: break-word; border: 1px solid #ddd; padding: 15px; border-radius: 4px; margin-bottom: 20px; background-color: #fff; max-height: 50vh; overflow-y: auto; }}
        .highlight {{ position: relative; border-radius: 3px; padding: 2px 4px; cursor: default; }}
        .tooltip {{
            visibility: hidden; opacity: 0; transition: opacity 0.2s;
            background: #333; color: #fff; text-align: left;
            border-radius: 4px; padding: 8px; position: absolute;
            z-index: 10; bottom: 125%; left: 50%;
            transform: translateX(-50%); font-size: 12px;
            width: max-content; max-width: 300px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        .highlight:hover .tooltip {{ visibility: visible; opacity: 1; }}
        .legend {{ margin-bottom: 20px; }}
        .legend-item {{ display: inline-flex; align-items: center; margin-right: 15px; font-size: 14px; }}
        .legend-color {{ width: 15px; height: 15px; border-radius: 3px; margin-right: 5px; }}
        .no-result {{ color: #999; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Extraction Visualization</h2>
            <div class="selectors">
                <div class="selector-container">
                    <label for="doc-selector">Document:</label>
                    <select id="doc-selector" class="selector"></select>
                </div>
                <div class="selector-container">
                    <label for="model-selector">Model:</label>
                    <select id="model-selector" class="selector"></select>
                </div>
            </div>
        </div>
        <div id="content-area">
            <div class="metadata-panel" id="metadata-panel"></div>
            <div class="legend" id="legend"></div>
            <div class="text-display" id="text-display"></div>
        </div>
        <div id="no-result-area" style="display: none;" class="no-result">
            No result available for this document/model combination.
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const organizedData = {organized_data_json};
            const docSelector = document.getElementById('doc-selector');
            const modelSelector = document.getElementById('model-selector');
            const metadataContainer = document.getElementById('metadata-panel');
            const legendContainer = document.getElementById('legend');
            const textContainer = document.getElementById('text-display');
            const contentArea = document.getElementById('content-area');
            const noResultArea = document.getElementById('no-result-area');

            const docIds = Object.keys(organizedData).sort();
            
            function populateDocSelector() {{
                docIds.forEach(docId => {{
                    const option = document.createElement('option');
                    option.value = docId;
                    option.textContent = docId;
                    docSelector.appendChild(option);
                }});
            }}

            function populateModelSelector(selectedDocId) {{
                modelSelector.innerHTML = '';
                const availableModels = Object.keys(organizedData[selectedDocId] || {{}}).sort();
                availableModels.forEach(modelId => {{
                    const option = document.createElement('option');
                    option.value = modelId;
                    option.textContent = modelId;
                    modelSelector.appendChild(option);
                }});
            }}

            function render() {{
                const selectedDocId = docSelector.value;
                const selectedModelId = modelSelector.value;
                const docData = organizedData[selectedDocId] && organizedData[selectedDocId][selectedModelId];

                if (!docData) {{
                    contentArea.style.display = 'none';
                    noResultArea.style.display = 'block';
                    return;
                }}
                
                contentArea.style.display = 'block';
                noResultArea.style.display = 'none';

                // Render Metadata
                let metadataHtml = '';
                if (docData.metadata) {{
                    for (const [key, value] of Object.entries(docData.metadata)) {{
                        const displayValue = typeof value === 'object' ? JSON.stringify(value) : value;
                        metadataHtml += `<strong>${{escapeHtml(key)}}:</strong> <code>${{escapeHtml(String(displayValue))}}</code><br>`;
                    }}
                }}
                metadataContainer.innerHTML = metadataHtml;

                // Render Legend
                legendContainer.innerHTML = '';
                for (const [cls, color] of Object.entries(docData.colorMap)) {{
                    const item = document.createElement('div');
                    item.className = 'legend-item';
                    item.innerHTML = `<div class="legend-color" style="background-color: ${{color}};"></div>${{cls}}`;
                    legendContainer.appendChild(item);
                }}

                // Render Text
                textContainer.innerHTML = buildHighlightedHtml(docData.text, docData.extractions, docData.colorMap);
            }}

            function buildHighlightedHtml(text, extractions, colorMap) {{
                let html = '';
                let lastIndex = 0;
                const sortedExtractions = extractions.sort((a, b) => (a.char_interval.start || 0) - (b.char_interval.start || 0));

                sortedExtractions.forEach(ext => {{
                    if (ext.char_interval) {{
                        html += escapeHtml(text.substring(lastIndex, ext.char_interval.start));
                        const color = colorMap[ext.extraction_class] || '#ccc';
                        
                        let tooltip = `<strong>${{escapeHtml(ext.extraction_class)}}</strong>`;
                        if (ext.attributes && Object.keys(ext.attributes).length > 0) {{
                            tooltip += '<hr style="margin: 4px 0; border-color: #555;">';
                            for (const [key, value] of Object.entries(ext.attributes)) {{
                                tooltip += `<div><em>${{escapeHtml(key)}}</em>: ${{escapeHtml(String(value))}}</div>`;
                            }}
                        }}

                        html += `<span class="highlight" style="background-color: ${{color}};">` +
                                `${{escapeHtml(text.substring(ext.char_interval.start, ext.char_interval.end))}}` +
                                `<span class="tooltip">${{tooltip}}</span></span>`;
                        lastIndex = ext.char_interval.end;
                    }}
                }});
                html += escapeHtml(text.substring(lastIndex));
                return html;
            }}

            function escapeHtml(unsafe) {{
                return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
            }}

            // --- Event Listeners ---
            docSelector.addEventListener('change', () => {{
                populateModelSelector(docSelector.value);
                render();
            }});
            modelSelector.addEventListener('change', render);

            // --- Initial Load ---
            if (docIds.length > 0) {{
                populateDocSelector();
                populateModelSelector(docIds[0]);
                render();
            }} else {{
                noResultArea.textContent = "No documents were provided for visualization.";
                noResultArea.style.display = 'block';
            }}
        }});
    </script>
</body>
</html>
""")


def _assign_colors(extractions: List[Extraction]) -> dict[str, str]:
    """Assigns a consistent color to each unique extraction class."""
    unique_classes = sorted(list({ext.extraction_class for ext in extractions}))
    return {cls: _PALETTE[i % len(_PALETTE)] for i, cls in enumerate(unique_classes)}


def visualize(docs_or_doc: Union[AnnotatedDocument, List[AnnotatedDocument]]) -> str:
    """
    Generates a single HTML visualization for one or more AnnotatedDocuments.
    """
    docs = [docs_or_doc] if isinstance(docs_or_doc, AnnotatedDocument) else docs_or_doc
    if not docs:
        return "<p>No documents to visualize.</p>"

    # nested dictionary: {doc_id: {model_name: data}}
    organized_data: Dict[str, Dict[str, Any]] = {}

    for i, doc in enumerate(docs):
        doc_id = doc.metadata.get("doc_id", f"Document_{i + 1}")
        model_name = doc.metadata.get("model_name", "Unknown_Model")

        if doc_id not in organized_data:
            organized_data[doc_id] = {}

        valid_extractions = [ext for ext in doc.extractions if ext.char_interval]
        color_map = _assign_colors(valid_extractions)

        organized_data[doc_id][model_name] = {
            "text": doc.text,
            "extractions": [ext.model_dump() for ext in valid_extractions],
            "colorMap": color_map,
            "metadata": doc.metadata,
        }

    return _HTML_TEMPLATE.format(organized_data_json=json.dumps(organized_data))
