"""
LangExtract MCP Server - Production Version
Extract structured information from unstructured text using Gemini/Ollama models

Deploy: Push to GitHub and deploy on fastmcp.cloud
"""

from fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import langextract as lx
import os
import tempfile
from pathlib import Path
from datetime import datetime
import hashlib

# Initialize FastMCP server
mcp = FastMCP("LangExtract")

# Result storage
RESULTS_STORE: Dict[str, lx.data.AnnotatedDocument] = {}

# ============================================================================
# CORE EXTRACTION TOOLS
# ============================================================================

@mcp.tool
async def extract_structured_data(
    ctx: Context,
    text: str,
    prompt_description: str,
    examples: List[Dict[str, Any]],
    model_id: str = "gemini-2.5-flash",
    extraction_passes: int = 1,
    max_workers: int = 10,
    max_char_buffer: int = 8000,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract structured information from text using LangExtract.
    
    Args:
        text: The input text to extract from
        prompt_description: Clear instructions for what to extract
        examples: List of example extractions (few-shot learning)
        model_id: Model to use (gemini-2.5-flash recommended)
        extraction_passes: Number of passes (1-5, more = higher recall)
        max_workers: Parallel workers (1-50, more = faster)
        max_char_buffer: Chunk size (1000-10000, smaller = more accurate)
        api_key: Optional API key (defaults to LANGEXTRACT_API_KEY env var)
    
    Example format:
    {
        "text": "Dr. Smith prescribed 50mg aspirin.",
        "extractions": [{
            "extraction_class": "medication",
            "extraction_text": "aspirin",
            "attributes": {"dosage": "50mg"}
        }]
    }
    """
    
    try:
        await ctx.info(f"🔍 Starting extraction with {model_id}")
        
        # Validate inputs
        if not text or not text.strip():
            return {'success': False, 'error': 'Text cannot be empty'}
        
        if not prompt_description or not prompt_description.strip():
            return {'success': False, 'error': 'Prompt description required'}
        
        if not examples or len(examples) == 0:
            return {
                'success': False, 
                'error': 'At least one example required',
                'hint': 'Use create_example_template to generate format'
            }
        
        # Convert examples to LangExtract format
        lx_examples = []
        for idx, ex in enumerate(examples):
            try:
                if 'text' not in ex or 'extractions' not in ex:
                    return {'success': False, 'error': f'Example {idx} missing text or extractions'}
                
                extractions = []
                for e in ex['extractions']:
                    if 'extraction_class' not in e or 'extraction_text' not in e:
                        return {'success': False, 'error': f'Example {idx} extraction missing required fields'}
                    
                    extractions.append(
                        lx.data.Extraction(
                            extraction_class=e['extraction_class'],
                            extraction_text=e['extraction_text'],
                            attributes=e.get('attributes', {}),
                            char_start=e.get('char_start', 0),
                            char_end=e.get('char_end', len(e.get('extraction_text', '')))
                        )
                    )
                
                lx_examples.append(lx.data.ExampleData(text=ex['text'], extractions=extractions))
                
            except Exception as e:
                return {'success': False, 'error': f'Error parsing example {idx}: {str(e)}'}
        
        await ctx.info(f"✅ Parsed {len(lx_examples)} examples")
        
        # Get API key
        final_api_key = api_key or os.environ.get('LANGEXTRACT_API_KEY')
        if not final_api_key:
            return {
                'success': False, 
                'error': 'LANGEXTRACT_API_KEY not set',
                'hint': 'Set environment variable or pass api_key parameter'
            }
        
        await ctx.info("🚀 Calling LangExtract API...")
        
        # Run extraction
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt_description,
            examples=lx_examples,
            model_id=model_id,
            api_key=final_api_key,
            extraction_passes=extraction_passes,
            max_workers=max_workers,
            max_char_buffer=max_char_buffer
        )
        
        # Convert results
        extractions_list = [
            {
                'extraction_class': e.extraction_class,
                'extraction_text': e.extraction_text,
                'attributes': e.attributes,
                'char_start': e.char_start,
                'char_end': e.char_end
            } 
            for e in result.extractions
        ]
        
        # Store result
        result_id = hashlib.md5(f"{text[:100]}{datetime.now().isoformat()}".encode()).hexdigest()
        RESULTS_STORE[result_id] = result
        
        await ctx.info(f"✨ Found {len(extractions_list)} entities")
        
        return {
            'success': True,
            'result_id': result_id,
            'total_extractions': len(extractions_list),
            'extractions': extractions_list,
            'metadata': {
                'model_id': model_id,
                'extraction_passes': extraction_passes,
                'text_length': len(text)
            }
        }
        
    except Exception as e:
        await ctx.error(f"Extraction failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@mcp.tool
async def extract_from_url(
    ctx: Context,
    url: str,
    prompt_description: str,
    examples: List[Dict[str, Any]],
    model_id: str = "gemini-2.5-flash",
    extraction_passes: int = 2,
    max_workers: int = 20
) -> Dict[str, Any]:
    """
    Extract structured information directly from a URL.
    
    Args:
        url: URL to fetch and extract from
        prompt_description: Extraction instructions
        examples: Few-shot examples
        model_id: Model to use
        extraction_passes: Number of passes (default 2 for URLs)
        max_workers: Parallel workers (default 20)
    """
    
    try:
        await ctx.info(f"🌐 Fetching: {url}")
        
        if not url.startswith(('http://', 'https://')):
            return {'success': False, 'error': 'Invalid URL'}
        
        # Convert examples
        lx_examples = []
        for ex in examples:
            extractions = [
                lx.data.Extraction(
                    extraction_class=e['extraction_class'],
                    extraction_text=e['extraction_text'],
                    attributes=e.get('attributes', {}),
                    char_start=e.get('char_start', 0),
                    char_end=e.get('char_end', len(e.get('extraction_text', '')))
                )
                for e in ex.get('extractions', [])
            ]
            lx_examples.append(lx.data.ExampleData(text=ex['text'], extractions=extractions))
        
        # Get API key
        api_key = os.environ.get('LANGEXTRACT_API_KEY')
        if not api_key:
            return {'success': False, 'error': 'LANGEXTRACT_API_KEY not set'}
        
        await ctx.info(f"🚀 Processing URL with {extraction_passes} passes...")
        
        # Extract from URL
        result = lx.extract(
            text_or_documents=url,
            prompt_description=prompt_description,
            examples=lx_examples,
            model_id=model_id,
            api_key=api_key,
            extraction_passes=extraction_passes,
            max_workers=max_workers
        )
        
        # Process results
        extractions_list = [
            {
                'extraction_class': e.extraction_class,
                'extraction_text': e.extraction_text,
                'attributes': e.attributes,
                'char_start': e.char_start,
                'char_end': e.char_end
            }
            for e in result.extractions
        ]
        
        result_id = hashlib.md5(f"{url}{datetime.now().isoformat()}".encode()).hexdigest()
        RESULTS_STORE[result_id] = result
        
        await ctx.info(f"✨ Found {len(extractions_list)} entities from URL")
        
        return {
            'success': True,
            'result_id': result_id,
            'url': url,
            'total_extractions': len(extractions_list),
            'extractions': extractions_list
        }
        
    except Exception as e:
        await ctx.error(f"URL extraction failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@mcp.tool
async def save_results_to_jsonl(
    ctx: Context,
    result_id: str,
    output_name: str = "extraction_results.jsonl"
) -> Dict[str, Any]:
    """
    Save extraction results to JSONL file.
    
    Args:
        result_id: The extraction result ID
        output_name: Output filename
    """
    
    try:
        if result_id not in RESULTS_STORE:
            return {'success': False, 'error': 'Result not found'}
        
        result = RESULTS_STORE[result_id]
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        
        await ctx.info(f"💾 Saving to {output_path}...")
        
        lx.io.save_annotated_documents([result], output_name=output_name, output_dir=str(output_dir))
        
        await ctx.info(f"✅ Saved {len(result.extractions)} extractions")
        
        return {
            'success': True,
            'file_path': str(output_path.absolute()),
            'total_extractions': len(result.extractions)
        }
        
    except Exception as e:
        await ctx.error(f"Save failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@mcp.tool
async def generate_visualization(
    ctx: Context,
    result_id: str,
    output_name: str = "visualization.html"
) -> Dict[str, Any]:
    """
    Generate interactive HTML visualization of extractions.
    
    Args:
        result_id: The extraction result ID
        output_name: Output HTML filename
    """
    
    try:
        if result_id not in RESULTS_STORE:
            return {'success': False, 'error': 'Result not found'}
        
        result = RESULTS_STORE[result_id]
        
        await ctx.info("🎨 Generating visualization...")
        
        # Save to temp JSONL
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
            lx.io.save_annotated_documents([result], output_name=os.path.basename(f.name), output_dir=os.path.dirname(f.name))
            jsonl_path = f.name
        
        # Generate HTML
        html_content = lx.visualize(jsonl_path)
        os.unlink(jsonl_path)
        
        html = html_content.data if hasattr(html_content, 'data') else html_content
        
        # Save HTML
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        await ctx.info(f"✨ Visualization saved to {output_path}")
        
        return {
            'success': True,
            'file_path': str(output_path.absolute()),
            'total_extractions': len(result.extractions),
            'instructions': 'Open HTML file in browser'
        }
        
    except Exception as e:
        await ctx.error(f"Visualization failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@mcp.tool
async def list_stored_results(ctx: Context) -> Dict[str, Any]:
    """List all extraction results in current session."""
    
    results_summary = [
        {
            'result_id': rid,
            'total_extractions': len(result.extractions),
            'classes': list(set(e.extraction_class for e in result.extractions))
        }
        for rid, result in RESULTS_STORE.items()
    ]
    
    return {
        'total_results': len(RESULTS_STORE),
        'results': results_summary
    }


@mcp.tool
async def get_extraction_details(
    ctx: Context,
    result_id: str
) -> Dict[str, Any]:
    """
    Get full details of a specific extraction result.
    
    Args:
        result_id: The extraction result ID
    """
    
    if result_id not in RESULTS_STORE:
        return {
            'success': False,
            'error': f'Result not found: {result_id}',
            'available_ids': list(RESULTS_STORE.keys())
        }
    
    result = RESULTS_STORE[result_id]
    
    extractions = [
        {
            'extraction_class': e.extraction_class,
            'extraction_text': e.extraction_text,
            'attributes': e.attributes,
            'char_start': e.char_start,
            'char_end': e.char_end
        }
        for e in result.extractions
    ]
    
    # Group by class
    by_class = {}
    for e in extractions:
        cls = e['extraction_class']
        if cls not in by_class:
            by_class[cls] = []
        by_class[cls].append(e)
    
    await ctx.info(f"📊 Retrieved {len(extractions)} extractions")
    
    return {
        'success': True,
        'result_id': result_id,
        'total_extractions': len(extractions),
        'extractions': extractions,
        'grouped_by_class': by_class,
        'statistics': {
            'classes': list(by_class.keys()),
            'count_per_class': {k: len(v) for k, v in by_class.items()}
        }
    }


@mcp.tool
async def create_example_template(
    ctx: Context,
    extraction_classes: List[str]
) -> Dict[str, Any]:
    """
    Generate template for creating extraction examples.
    
    Args:
        extraction_classes: List of classes to extract (e.g., ["person", "medication"])
    """
    
    template = [{
        "text": "<Your example text here>",
        "extractions": [
            {
                "extraction_class": cls,
                "extraction_text": f"<example {cls}>",
                "attributes": {"example_key": "example_value"}
            }
            for cls in extraction_classes
        ]
    }]
    
    usage = f"""
Example:
{{
    "text": "Dr. Smith prescribed 50mg aspirin.",
    "extractions": [
        {{"extraction_class": "{extraction_classes[0] if extraction_classes else 'entity'}", "extraction_text": "Dr. Smith", "attributes": {{"role": "doctor"}}}},
        {{"extraction_class": "{extraction_classes[1] if len(extraction_classes) > 1 else 'entity'}", "extraction_text": "aspirin", "attributes": {{"dosage": "50mg"}}}}
    ]
}}
"""
    
    return {
        'template': template,
        'extraction_classes': extraction_classes,
        'usage_example': usage
    }


@mcp.tool
async def get_supported_models(ctx: Context) -> Dict[str, Any]:
    """Get list of supported models and recommendations."""
    
    return {
        'gemini_models': {
            'gemini-2.5-flash': {
                'description': 'Fast and cost-effective (RECOMMENDED)',
                'cost': 'Low',
                'speed': 'Very Fast',
                'best_for': 'General extraction, large volumes, production'
            },
            'gemini-2.5-pro': {
                'description': 'Advanced reasoning for complex tasks',
                'cost': 'Higher',
                'speed': 'Moderate',
                'best_for': 'Complex medical/legal text, high accuracy needs'
            }
        },
        'recommendations': {
            'default': 'gemini-2.5-flash',
            'high_accuracy': 'gemini-2.5-pro',
            'production': 'gemini-2.5-flash with extraction_passes=2-3'
        }
    }

# ============================================================================
# SERVER METADATA
# ============================================================================

__all__ = ["mcp"]

if __name__ == "__main__":
    mcp.run()
