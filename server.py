"""LangExtract MCP Server"""
from fastmcp import FastMCP
import langextract as lx
import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path

mcp = FastMCP("LangExtract")
RESULTS_STORE = {}

@mcp.tool()
def extract_structured_data(text: str, prompt_description: str, examples: List[Dict[str, Any]], model_id: str = "gemini-2.5-flash", extraction_passes: int = 1, max_workers: int = 10) -> Dict[str, Any]:
    """Extract structured information from text."""
    try:
        lx_examples = []
        for ex in examples:
            extractions = [
                lx.data.Extraction(
                    extraction_class=e.get('extraction_class', ''),
                    extraction_text=e.get('extraction_text', ''),
                    attributes=e.get('attributes', {}),
                    char_start=e.get('char_start', 0),
                    char_end=e.get('char_end', len(e.get('extraction_text', '')))
                ) 
                for e in ex.get('extractions', [])
            ]
            lx_examples.append(lx.data.ExampleData(text=ex.get('text', ''), extractions=extractions))
        
        api_key = os.environ.get('LANGEXTRACT_API_KEY')
        if not api_key:
            return {'success': False, 'error': 'LANGEXTRACT_API_KEY not set'}
        
        result = lx.extract(text_or_documents=text, prompt_description=prompt_description, examples=lx_examples, model_id=model_id, api_key=api_key, extraction_passes=extraction_passes, max_workers=max_workers)
        
        extractions_list = [{'extraction_class': e.extraction_class, 'extraction_text': e.extraction_text, 'attributes': e.attributes, 'char_start': e.char_start, 'char_end': e.char_end} for e in result.extractions]
        
        import hashlib
        from datetime import datetime
        result_id = hashlib.md5(f"{text[:100]}{datetime.now().isoformat()}".encode()).hexdigest()
        RESULTS_STORE[result_id] = result
        
        return {'success': True, 'result_id': result_id, 'extractions': extractions_list, 'total_extractions': len(extractions_list)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@mcp.tool()
def extract_from_url(url: str, prompt_description: str, examples: List[Dict[str, Any]], model_id: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """Extract from URL."""
    return extract_structured_data(url, prompt_description, examples, model_id, 2, 20)

@mcp.tool()
def save_results_to_jsonl(result_id: str, output_name: str = "extraction_results.jsonl") -> Dict[str, Any]:
    """Save results to JSONL."""
    try:
        if result_id not in RESULTS_STORE:
            return {'success': False, 'error': 'Result not found'}
        result = RESULTS_STORE[result_id]
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        lx.io.save_annotated_documents([result], output_name=output_name, output_dir=str(output_dir))
        return {'success': True, 'file_path': str(output_path.absolute())}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@mcp.tool()
def generate_visualization(result_id: str, output_name: str = "visualization.html") -> Dict[str, Any]:
    """Generate HTML visualization."""
    try:
        if result_id not in RESULTS_STORE:
            return {'success': False, 'error': 'Result not found'}
        result = RESULTS_STORE[result_id]
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
            lx.io.save_annotated_documents([result], output_name=os.path.basename(f.name), output_dir=os.path.dirname(f.name))
            jsonl_path = f.name
        html_content = lx.visualize(jsonl_path)
        os.unlink(jsonl_path)
        html = html_content.data if hasattr(html_content, 'data') else html_content
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return {'success': True, 'file_path': str(output_path.absolute())}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@mcp.tool()
def list_stored_results() -> Dict[str, Any]:
    """List all results."""
    return {'total_results': len(RESULTS_STORE), 'results': [{'result_id': rid, 'total_extractions': len(r.extractions)} for rid, r in RESULTS_STORE.items()]}

@mcp.tool()
def get_extraction_details(result_id: str) -> Dict[str, Any]:
    """Get extraction details."""
    if result_id not in RESULTS_STORE:
        return {'success': False, 'error': 'Result not found'}
    result = RESULTS_STORE[result_id]
    extractions = [{'extraction_class': e.extraction_class, 'extraction_text': e.extraction_text, 'attributes': e.attributes, 'char_start': e.char_start, 'char_end': e.char_end} for e in result.extractions]
    return {'success': True, 'result_id': result_id, 'extractions': extractions}

@mcp.tool()
def create_example_template(extraction_classes: List[str]) -> Dict[str, Any]:
    """Generate example template."""
    template = [{
        "text": "<example text>",
        "extractions": [{
            "extraction_class": c,
            "extraction_text": f"<text for {c}>",
            "attributes": {},
            "char_start": 0,
            "char_end": 0
        } for c in extraction_classes]
    }]
    return {'template': template}

@mcp.tool()
def get_supported_models() -> Dict[str, Any]:
    """Get supported models."""
    return {'gemini_models': {'gemini-2.5-flash': {'description': 'Fast (recommended)', 'cost': 'Low'}, 'gemini-2.5-pro': {'description': 'Advanced', 'cost': 'Higher'}}, 'recommendations': {'default': 'gemini-2.5-flash'}}

if __name__ == "__main__":
    mcp.run()
