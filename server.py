"""
LangExtract MCP Server - Enhanced for Research Context Extraction
Extract comprehensive research context with full preservation of nuances and relationships

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
import pandas as pd
import json

# Initialize FastMCP server
mcp = FastMCP("LangExtract-ResearchContext")

# Result storage
RESULTS_STORE: Dict[str, lx.data.AnnotatedDocument] = {}

# ============================================================================
# RESEARCH CONTEXT EXTRACTION EXAMPLES
# ============================================================================

RESEARCH_CONTEXT_EXAMPLES = [
    # Example 1: Citation + Method + Constraint (interconnected)
    {
        "text": "Jensen & Sigmund (2011) introduced topology optimization for photonics using density-based methods, which converges well with accurate gradients but requires minimum linewidth ≥100nm for TSMC fabrication.",
        "extractions": [
            {
                "extraction_class": "CITATIONS_AND_REFERENCES",
                "extraction_text": "Jensen & Sigmund (2011)",
                "attributes": {
                    "category": "CITATIONS_AND_REFERENCES",
                    "subcategory": "primary_sources",
                    "element_name": "Jensen2011",
                    "citation_key": "Jensen2011",
                    "citation_authors": "Jensen,Sigmund",
                    "citation_year": "2011",
                    "citation_type": "journal_article",
                    "citation_url": "https://doi.org/10.1364/OE.19.008451",
                    "confidence_level": "certain",
                    "source_context": "Jensen & Sigmund (2011) introduced topology optimization for photonics using density-based methods",
                    "related_to": "density_based_topology,minimum_linewidth",
                    "notes": "Foundational paper for photonic topology optimization"
                }
            },
            {
                "extraction_class": "CURRENT_APPROACHES",
                "extraction_text": "density-based topology optimization",
                "attributes": {
                    "category": "CURRENT_APPROACHES",
                    "subcategory": "method_classification",
                    "element_name": "density_based_topology",
                    "attribute_key": "type",
                    "attribute_value": "gradient-based optimization",
                    "citation_key": "Jensen2011",
                    "evidence_type": "empirical",
                    "confidence_level": "high",
                    "impact_score": "9",
                    "source_context": "density-based methods, which converges well with accurate gradients",
                    "related_to": "Jensen2011,minimum_linewidth",
                    "notes": "Strength: accurate gradients. Links to manufacturing constraints."
                }
            },
            {
                "extraction_class": "CONSTRAINTS",
                "extraction_text": "minimum linewidth ≥100nm",
                "attributes": {
                    "category": "CONSTRAINTS",
                    "subcategory": "physical_constraints",
                    "element_name": "minimum_linewidth",
                    "attribute_key": "value",
                    "attribute_value": "≥100nm",
                    "constraint_type": "geometric",
                    "constraint_source": "TSMC foundry",
                    "constraint_enforcement": "automatic_DRC_check",
                    "confidence_level": "certain",
                    "impact_score": "10",
                    "source_context": "requires minimum linewidth ≥100nm for TSMC fabrication",
                    "related_to": "density_based_topology,TSMC_process",
                    "notes": "Hard constraint from manufacturing physics. Non-negotiable."
                }
            }
        ]
    },
    
    # Example 2: Domain Hierarchy + Interdisciplinary Connection
    {
        "text": "Integrated photonics, a subfield of optical engineering, increasingly leverages computational methods from optimization theory to design on-chip devices.",
        "extractions": [
            {
                "extraction_class": "DOMAIN_CONTEXT",
                "extraction_text": "Integrated photonics",
                "attributes": {
                    "category": "DOMAIN_CONTEXT",
                    "subcategory": "domain_hierarchy",
                    "element_name": "integrated_photonics",
                    "domain_hierarchy": "Optics->Photonics->Integrated Photonics",
                    "domain_level": "2",
                    "parent_domain": "Photonics",
                    "child_domains": "Silicon Photonics,III-V Photonics",
                    "confidence_level": "certain",
                    "source_context": "Integrated photonics, a subfield of optical engineering",
                    "related_to": "optical_engineering,computational_photonics",
                    "notes": "Core application domain"
                }
            },
            {
                "extraction_class": "DOMAIN_CONTEXT",
                "extraction_text": "computational methods from optimization theory",
                "attributes": {
                    "category": "DOMAIN_CONTEXT",
                    "subcategory": "interdisciplinary_connections",
                    "element_name": "optimization_to_photonics",
                    "relationship_type": "methodology_transfer",
                    "relationship_target": "integrated_photonics",
                    "cross_domain_refs": "Mathematics->Optimization",
                    "confidence_level": "high",
                    "source_context": "leverages computational methods from optimization theory to design on-chip devices",
                    "related_to": "integrated_photonics,density_based_topology",
                    "notes": "Cross-domain methodological bridge"
                }
            }
        ]
    },
    
    # Example 3: Resource + Requirement + Trade-off
    {
        "text": "FDTD simulations using Lumerical require HPC clusters (128+ cores) to achieve convergence in reasonable time, trading computational cost for accuracy.",
        "extractions": [
            {
                "extraction_class": "RESOURCES",
                "extraction_text": "Lumerical",
                "attributes": {
                    "category": "RESOURCES",
                    "subcategory": "software_tools",
                    "element_name": "FDTD_Solutions",
                    "resource_name": "Lumerical FDTD",
                    "resource_url": "https://www.lumerical.com/products/fdtd/",
                    "resource_type": "commercial_software",
                    "confidence_level": "certain",
                    "source_context": "FDTD simulations using Lumerical",
                    "related_to": "HPC_cluster,time_accuracy_tradeoff",
                    "notes": "Industry standard electromagnetic solver"
                }
            },
            {
                "extraction_class": "RESOURCES",
                "extraction_text": "HPC clusters (128+ cores)",
                "attributes": {
                    "category": "RESOURCES",
                    "subcategory": "computational_resources",
                    "element_name": "HPC_cluster",
                    "attribute_key": "specifications",
                    "attribute_value": "128+ cores minimum",
                    "confidence_level": "high",
                    "impact_score": "8",
                    "source_context": "require HPC clusters (128+ cores) to achieve convergence in reasonable time",
                    "related_to": "FDTD_Solutions,time_accuracy_tradeoff",
                    "notes": "Required for practical simulation times"
                }
            },
            {
                "extraction_class": "TRADE_OFFS",
                "extraction_text": "trading computational cost for accuracy",
                "attributes": {
                    "category": "TRADE_OFFS",
                    "subcategory": "technical_tensions",
                    "element_name": "time_accuracy_tradeoff",
                    "relationship_type": "competing_objectives",
                    "relationship_target": "computational_cost,simulation_accuracy",
                    "confidence_level": "certain",
                    "source_context": "trading computational cost for accuracy",
                    "related_to": "FDTD_Solutions,HPC_cluster",
                    "notes": "Fundamental tension in numerical simulation"
                }
            }
        ]
    },
    
    # Example 4: Problem + Gap + Requirement
    {
        "text": "Current inverse design methods fail to guarantee manufacturability constraints, creating a gap between optimized designs and fabricable devices. A solution must enforce physical limits during optimization.",
        "extractions": [
            {
                "extraction_class": "PROBLEM_DEFINITION",
                "extraction_text": "fail to guarantee manufacturability constraints",
                "attributes": {
                    "category": "PROBLEM_DEFINITION",
                    "subcategory": "failure_modes",
                    "element_name": "manufacturability_failure",
                    "attribute_key": "what_fails",
                    "attribute_value": "constraint enforcement",
                    "evidence_type": "empirical",
                    "confidence_level": "high",
                    "impact_score": "10",
                    "source_context": "Current inverse design methods fail to guarantee manufacturability constraints",
                    "related_to": "design_fab_gap,constraint_enforcement_requirement",
                    "notes": "Critical failure mode affecting all current approaches"
                }
            },
            {
                "extraction_class": "PROBLEM_DEFINITION",
                "extraction_text": "gap between optimized designs and fabricable devices",
                "attributes": {
                    "category": "PROBLEM_DEFINITION",
                    "subcategory": "gap_analysis",
                    "element_name": "design_fab_gap",
                    "attribute_key": "delta",
                    "attribute_value": "unmanufacturable outputs",
                    "confidence_level": "certain",
                    "impact_score": "10",
                    "source_context": "creating a gap between optimized designs and fabricable devices",
                    "related_to": "manufacturability_failure,constraint_enforcement_requirement",
                    "notes": "Root cause of design-to-fabrication failure"
                }
            },
            {
                "extraction_class": "REQUIREMENTS",
                "extraction_text": "must enforce physical limits during optimization",
                "attributes": {
                    "category": "REQUIREMENTS",
                    "subcategory": "functional_requirements",
                    "element_name": "constraint_enforcement_requirement",
                    "attribute_key": "specification",
                    "attribute_value": "real-time constraint enforcement",
                    "confidence_level": "certain",
                    "impact_score": "10",
                    "source_context": "A solution must enforce physical limits during optimization",
                    "related_to": "manufacturability_failure,design_fab_gap",
                    "notes": "Hard requirement derived from problem analysis"
                }
            }
        ]
    },
    
    # Example 5: Implicit Constraint + Standards Reference
    {
        "text": "Devices operating at 1550nm wavelength for telecom applications must comply with ITU-T standards, implicitly requiring temperature stability from -40°C to 85°C.",
        "extractions": [
            {
                "extraction_class": "CONSTRAINTS",
                "extraction_text": "comply with ITU-T standards",
                "attributes": {
                    "category": "CONSTRAINTS",
                    "subcategory": "regulatory_constraints",
                    "element_name": "ITU_compliance",
                    "constraint_type": "regulatory",
                    "constraint_source": "ITU-T",
                    "constraint_enforcement": "mandatory_for_telecom",
                    "citation_url": "https://www.itu.int/",
                    "confidence_level": "certain",
                    "impact_score": "9",
                    "source_context": "must comply with ITU-T standards",
                    "related_to": "telecom_wavelength,temperature_stability",
                    "notes": "International telecom standards body"
                }
            },
            {
                "extraction_class": "CONSTRAINTS",
                "extraction_text": "temperature stability from -40°C to 85°C",
                "attributes": {
                    "category": "CONSTRAINTS",
                    "subcategory": "environmental_constraints",
                    "element_name": "temperature_stability",
                    "attribute_key": "range",
                    "attribute_value": "-40°C to 85°C",
                    "constraint_type": "environmental",
                    "constraint_source": "ITU_compliance",
                    "constraint_dependencies": "ITU_compliance",
                    "confidence_level": "high",
                    "impact_score": "8",
                    "source_context": "implicitly requiring temperature stability from -40°C to 85°C",
                    "related_to": "ITU_compliance",
                    "notes": "IMPLICIT requirement derived from standards. Critical for reliability."
                }
            }
        ]
    }
]

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
                'hint': 'Use create_example_template or get_research_examples for examples'
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
                            attributes=e.get('attributes', {})
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
        
        # Convert results - safely extract all attributes
        extractions_list = []
        for e in result.extractions:
            extraction_dict = {
                'extraction_class': e.extraction_class,
                'extraction_text': e.extraction_text,
                'attributes': e.attributes if hasattr(e, 'attributes') else {}
            }
            
            # Handle char_interval
            if hasattr(e, 'char_interval') and e.char_interval is not None:
                try:
                    if hasattr(e.char_interval, '__iter__'):
                        interval_list = list(e.char_interval)
                        extraction_dict['char_start'] = interval_list[0]
                        extraction_dict['char_end'] = interval_list[1]
                    elif hasattr(e.char_interval, 'start') and hasattr(e.char_interval, 'end'):
                        extraction_dict['char_start'] = e.char_interval.start
                        extraction_dict['char_end'] = e.char_interval.end
                except:
                    pass
            
            extractions_list.append(extraction_dict)
        
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
        return {'success': False, 'error': str(e), 'error_type': type(e).__name__}


@mcp.tool
async def extract_research_context(
    ctx: Context,
    text: str,
    model_id: str = "gemini-2.5-pro",
    extraction_passes: int = 5,
    max_workers: int = 30,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract comprehensive research context with full preservation of nuances and relationships.
    
    This is a specialized tool for research papers/documentation that:
    - Extracts all 10 categories (domains, methods, constraints, citations, etc.)
    - Preserves source context and relationships
    - Surfaces implicit assumptions
    - Maintains semantic connections
    
    Args:
        text: Research text to extract from
        model_id: Model to use (gemini-2.5-pro recommended for accuracy)
        extraction_passes: Number of passes (5 recommended)
        max_workers: Parallel workers (30 recommended)
        api_key: Optional API key
    """
    
    prompt = """
    Extract ALL research context elements from this text:
    - Domain hierarchies and interdisciplinary connections (DOMAIN_CONTEXT)
    - Methods, approaches, and techniques with citations (CURRENT_APPROACHES)
    - ALL constraints: physical, technical, regulatory, economic, environmental, temporal (CONSTRAINTS)
    - Citations and references: papers, standards, code, datasets (CITATIONS_AND_REFERENCES)
    - Resources: software, hardware, facilities, funding (RESOURCES)
    - Problems, gaps, and failure modes (PROBLEM_DEFINITION)
    - Requirements and success criteria (REQUIREMENTS)
    - Trade-offs and competing objectives (TRADE_OFFS)
    - Relationships between all elements (RELATIONSHIPS)
    - Solution spaces and opportunities (SOLUTION_SPACE)
    
    CRITICAL REQUIREMENTS:
    1. Preserve the EXACT source context for each extraction
    2. Link related extractions using element names in 'related_to'
    3. Surface IMPLICIT assumptions and constraints
    4. Maintain semantic connections
    5. Capture nuances and qualifiers (e.g., "non-negotiable", "typically", "must")
    6. Include evidence type and confidence level
    7. Extract ALL citations with full bibliographic information
    
    Think of this as building a knowledge graph where every node (extraction) 
    retains its original context and edges (relationships) to other nodes.
    """
    
    await ctx.info("🔬 Starting comprehensive research context extraction...")
    await ctx.info(f"📝 Text length: {len(text)} characters")
    await ctx.info(f"🎯 Using {len(RESEARCH_CONTEXT_EXAMPLES)} specialized examples")
    
    # Call the main extraction function
    result = await extract_structured_data(
        ctx=ctx,
        text=text,
        prompt_description=prompt,
        examples=RESEARCH_CONTEXT_EXAMPLES,
        model_id=model_id,
        extraction_passes=extraction_passes,
        max_workers=max_workers,
        max_char_buffer=10000,  # Large buffer to preserve context
        api_key=api_key
    )
    
    if result.get('success'):
        await ctx.info("✅ Research context extraction complete")
        await ctx.info(f"📊 Total extractions: {result['total_extractions']}")
        
        # Count by category
        categories = {}
        for ext in result['extractions']:
            cat = ext.get('attributes', {}).get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        await ctx.info(f"📁 Categories found: {list(categories.keys())}")
        result['category_breakdown'] = categories
    
    return result


@mcp.tool
async def export_to_research_csv(
    ctx: Context,
    result_id: str,
    output_name: str = "research_context.csv"
) -> Dict[str, Any]:
    """
    Export extractions to 30-column research context CSV schema.
    
    This converts LangExtract results to the comprehensive research CSV format with:
    - All 30 columns (id, category, subcategory, element_name, etc.)
    - Source context preservation
    - Relationship linking (converts names to IDs)
    - Full bibliographic information
    - Constraint metadata
    
    Args:
        result_id: The extraction result ID
        output_name: Output CSV filename
    """
    
    try:
        if result_id not in RESULTS_STORE:
            return {
                'success': False, 
                'error': f'Result not found: {result_id}',
                'available_ids': list(RESULTS_STORE.keys())
            }
        
        result = RESULTS_STORE[result_id]
        
        await ctx.info(f"📊 Converting {len(result.extractions)} extractions to CSV...")
        
        rows = []
        extraction_map = {}  # Map element_name to ID
        
        # First pass: Create rows and build ID map
        for idx, e in enumerate(result.extractions, start=1):
            attrs = e.attributes if hasattr(e, 'attributes') else {}
            
            # Build complete row
            row = {
                'id': idx,
                'category': attrs.get('category', ''),
                'subcategory': attrs.get('subcategory', ''),
                'element_name': attrs.get('element_name', f"element_{idx}"),
                'relationship_type': attrs.get('relationship_type', ''),
                'relationship_target': attrs.get('relationship_target', ''),
                'attribute_key': attrs.get('attribute_key', ''),
                'attribute_value': attrs.get('attribute_value', ''),
                'evidence_type': attrs.get('evidence_type', ''),
                'confidence_level': attrs.get('confidence_level', ''),
                'temporal_marker': attrs.get('temporal_marker', ''),
                'impact_score': attrs.get('impact_score', ''),
                'citation_key': attrs.get('citation_key', ''),
                'citation_url': attrs.get('citation_url', ''),
                'citation_authors': attrs.get('citation_authors', ''),
                'citation_year': attrs.get('citation_year', ''),
                'citation_type': attrs.get('citation_type', ''),
                'resource_name': attrs.get('resource_name', ''),
                'resource_url': attrs.get('resource_url', ''),
                'resource_type': attrs.get('resource_type', ''),
                'domain_hierarchy': attrs.get('domain_hierarchy', ''),
                'domain_level': attrs.get('domain_level', ''),
                'parent_domain': attrs.get('parent_domain', ''),
                'child_domains': attrs.get('child_domains', ''),
                'cross_domain_refs': attrs.get('cross_domain_refs', ''),
                'constraint_type': attrs.get('constraint_type', ''),
                'constraint_source': attrs.get('constraint_source', ''),
                'constraint_enforcement': attrs.get('constraint_enforcement', ''),
                'constraint_dependencies': attrs.get('constraint_dependencies', ''),
                'source_context': attrs.get('source_context', e.extraction_text),
                'related_to': attrs.get('related_to', ''),
                'notes': attrs.get('notes', '')
            }
            
            rows.append(row)
            element_name = attrs.get('element_name', f"element_{idx}")
            extraction_map[element_name] = idx
        
        # Second pass: Resolve relationships
        for row in rows:
            if row['related_to']:
                related_names = [name.strip() for name in row['related_to'].split(',')]
                related_ids = []
                for name in related_names:
                    if name in extraction_map:
                        related_ids.append(str(extraction_map[name]))
                
                if related_ids:
                    if row['relationship_target']:
                        row['relationship_target'] += ',' + ','.join(related_ids)
                    else:
                        row['relationship_target'] = ','.join(related_ids)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Save to CSV
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        await ctx.info(f"✅ Saved to {output_path}")
        
        # Validation stats
        stats = {
            'total_extractions': len(df),
            'with_source_context': (df['source_context'].str.len() > 0).sum(),
            'with_relationships': (df['relationship_target'].str.len() > 0).sum(),
            'with_citations': (df['citation_key'].str.len() > 0).sum(),
            'categories_covered': df['category'].nunique(),
            'category_breakdown': df['category'].value_counts().to_dict()
        }
        
        await ctx.info(f"📊 Context preserved: {stats['with_source_context']} ({stats['with_source_context']/stats['total_extractions']*100:.1f}%)")
        await ctx.info(f"🔗 Relationships linked: {stats['with_relationships']}")
        
        return {
            'success': True,
            'file_path': str(output_path.absolute()),
            'statistics': stats
        }
        
    except Exception as e:
        await ctx.error(f"CSV export failed: {str(e)}")
        return {'success': False, 'error': str(e)}


@mcp.tool
async def get_research_examples(ctx: Context) -> Dict[str, Any]:
    """
    Get the research context extraction examples.
    
    Returns the 5 comprehensive examples that train the model to:
    - Extract all 10 research categories
    - Preserve source context
    - Link related extractions
    - Surface implicit information
    - Maintain relationships
    """
    
    return {
        'total_examples': len(RESEARCH_CONTEXT_EXAMPLES),
        'examples': RESEARCH_CONTEXT_EXAMPLES,
        'categories_covered': [
            'CITATIONS_AND_REFERENCES',
            'CURRENT_APPROACHES',
            'CONSTRAINTS',
            'DOMAIN_CONTEXT',
            'RESOURCES',
            'TRADE_OFFS',
            'PROBLEM_DEFINITION',
            'REQUIREMENTS'
        ],
        'usage': 'Use these examples with extract_research_context or extract_structured_data'
    }


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
                    attributes=e.get('attributes', {})
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
        extractions_list = []
        for e in result.extractions:
            extraction_dict = {
                'extraction_class': e.extraction_class,
                'extraction_text': e.extraction_text,
                'attributes': e.attributes if hasattr(e, 'attributes') else {}
            }
            
            if hasattr(e, 'char_interval') and e.char_interval is not None:
                try:
                    if hasattr(e.char_interval, '__iter__'):
                        interval_list = list(e.char_interval)
                        extraction_dict['char_start'] = interval_list[0]
                        extraction_dict['char_end'] = interval_list[1]
                    elif hasattr(e.char_interval, 'start') and hasattr(e.char_interval, 'end'):
                        extraction_dict['char_start'] = e.char_interval.start
                        extraction_dict['char_end'] = e.char_interval.end
                except:
                    pass
            
            extractions_list.append(extraction_dict)
        
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
    """Save extraction results to JSONL file."""
    
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
    """Generate interactive HTML visualization of extractions."""
    
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
    """Get full details of a specific extraction result."""
    
    if result_id not in RESULTS_STORE:
        return {
            'success': False,
            'error': f'Result not found: {result_id}',
            'available_ids': list(RESULTS_STORE.keys())
        }
    
    result = RESULTS_STORE[result_id]
    
    extractions = []
    for e in result.extractions:
        extraction_dict = {
            'extraction_class': e.extraction_class,
            'extraction_text': e.extraction_text,
            'attributes': e.attributes if hasattr(e, 'attributes') else {}
        }
        
        if hasattr(e, 'char_interval') and e.char_interval is not None:
            try:
                if hasattr(e.char_interval, '__iter__'):
                    interval_list = list(e.char_interval)
                    extraction_dict['char_start'] = interval_list[0]
                    extraction_dict['char_end'] = interval_list[1]
                elif hasattr(e.char_interval, 'start') and hasattr(e.char_interval, 'end'):
                    extraction_dict['char_start'] = e.char_interval.start
                    extraction_dict['char_end'] = e.char_interval.end
            except:
                pass
        
        extractions.append(extraction_dict)
    
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
    """Generate template for creating extraction examples."""
    
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
                'description': 'Fast and cost-effective',
                'cost': 'Low',
                'speed': 'Very Fast',
                'best_for': 'General extraction, large volumes'
            },
            'gemini-2.5-pro': {
                'description': 'Advanced reasoning for complex tasks (RECOMMENDED for research)',
                'cost': 'Higher',
                'speed': 'Moderate',
                'best_for': 'Research papers, complex context, implicit information'
            }
        },
        'recommendations': {
            'research_extraction': 'gemini-2.5-pro with extraction_passes=5',
            'general_use': 'gemini-2.5-flash with extraction_passes=2-3',
            'high_volume': 'gemini-2.5-flash with extraction_passes=1'
        }
    }

# ============================================================================
# SERVER METADATA
# ============================================================================

__all__ = ["mcp"]

if __name__ == "__main__":
    mcp.run()
