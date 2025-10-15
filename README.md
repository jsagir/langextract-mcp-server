#Mindrian Speficic  LangExtract MCP Server - Enhanced for Research Context Extraction

**MCP server for comprehensive research context extraction using LangExtract and Gemini AI.**

Extract structured research information with full context preservation, relationship linking, and implicit assumption surfacing.

## 🎯 What's New: Research Context Extraction

This enhanced version adds specialized tools for extracting comprehensive research context from papers, documentation, and technical text:

- **10 Research Categories**: Domains, Methods, Constraints, Citations, Resources, Problems, Requirements, Trade-offs, Relationships, Solutions
- **30-Column CSV Schema**: Complete research context with full metadata
- **Context Preservation**: Original text spans maintained for every extraction
- **Relationship Linking**: Automatic connection of related extractions
- **Implicit Information**: Surfaces unstated assumptions and constraints
- **Full Bibliographic Data**: Complete citation extraction with DOIs, authors, years

## 🔧 Tools Available

### Core Tools
1. **`extract_structured_data`** - Main extraction from text (original functionality)
2. **`extract_from_url`** - Extract directly from URLs

### 🆕 Research-Specific Tools
3. **`extract_research_context`** - Specialized research extraction with 5 comprehensive examples
4. **`export_to_research_csv`** - Export to 30-column research CSV schema
5. **`get_research_examples`** - Get the 5 research extraction examples

### Output & Analysis
6. **`save_results_to_jsonl`** - Save results to JSONL format
7. **`generate_visualization`** - Create interactive HTML visualization
8. **`list_stored_results`** - List all extraction results
9. **`get_extraction_details`** - Get detailed extraction info

### Utilities
10. **`create_example_template`** - Generate example templates
11. **`get_supported_models`** - List available models

## 🚀 Quick Start

### 1. Get Gemini API Key

Visit: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

Click "Create API key" and copy it.

### 2. Deploy on FastMCP Cloud

- Go to [https://fastmcp.com/dashboard](https://fastmcp.com/dashboard)
- Sign in with GitHub
- Click "Create New Project"
- Select this repository
- Configure:
  - **Server File**: `server.py`
  - **Environment Variable**:
    - Name: `LANGEXTRACT_API_KEY`
    - Value: (paste your Gemini API key)
- Click "Deploy"
- Copy your deployment URL: `https://your-project.fastmcp.cloud`

### 3. Configure Claude Desktop

**Config file location:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add this:

```json
{
  "mcpServers": {
    "langextract-research": {
      "url": "https://your-project.fastmcp.cloud"
    }
  }
}
```

Replace `your-project.fastmcp.cloud` with your actual URL.

**Restart Claude Desktop after saving.**

## 📖 Usage Examples

### Example 1: Extract Research Context (Recommended for Papers)

```
Extract complete research context from this paper abstract:

"Jensen & Sigmund (2011) introduced topology optimization for photonics 
using density-based methods, which converges well with accurate gradients 
but requires minimum linewidth ≥100nm for TSMC fabrication. Current inverse 
design methods fail to guarantee manufacturability constraints, creating a 
gap between optimized designs and fabricable devices."

Use extract_research_context with model gemini-2.5-pro
```

This will extract:
- **Citations**: Jensen2011 with full bibliographic info
- **Methods**: density-based topology optimization
- **Constraints**: minimum linewidth ≥100nm (TSMC)
- **Problems**: manufacturability failure modes
- **Relationships**: Links between all elements

### Example 2: Export to Research CSV

```
After extraction, export the results to CSV:

Use export_to_research_csv with result_id: [the result ID from previous extraction]
Output file: "my_paper_context.csv"
```

This creates a 30-column CSV with:
- All extractions with source context preserved
- Relationship links (IDs)
- Full metadata (citations, constraints, resources)
- Category breakdown

### Example 3: View Research Examples

```
Show me the research extraction examples

Use get_research_examples
```

Returns the 5 comprehensive examples that train the model.

### Example 4: Custom Extraction

```
Extract people and medications from this clinical note:
"Dr. Sarah Johnson prescribed 50mg aspirin to patient John Doe."

Use extract_structured_data with examples:
- Person: "Dr. Smith" with role="doctor"
- Medication: "aspirin" with dosage="50mg"
```

## 🎓 Research CSV Schema

The 30-column schema captures complete research context:

### Core Fields
- `id`, `category`, `subcategory`, `element_name`
- `relationship_type`, `relationship_target`
- `attribute_key`, `attribute_value`

### Evidence & Confidence
- `evidence_type`, `confidence_level`
- `temporal_marker`, `impact_score`

### Citations
- `citation_key`, `citation_url`, `citation_authors`
- `citation_year`, `citation_type`

### Resources
- `resource_name`, `resource_url`, `resource_type`

### Domain Hierarchy
- `domain_hierarchy`, `domain_level`
- `parent_domain`, `child_domains`, `cross_domain_refs`

### Constraints
- `constraint_type`, `constraint_source`
- `constraint_enforcement`, `constraint_dependencies`

### Context Preservation
- `source_context` - Original text span
- `related_to` - Linked element names
- `notes` - Qualifiers and nuances

## 📊 Research Categories

The system extracts 10 comprehensive categories:

1. **DOMAIN_CONTEXT** - Field hierarchies, terminology, interdisciplinary connections
2. **CURRENT_APPROACHES** - Methods, techniques, performance profiles
3. **CONSTRAINTS** - Physical, technical, regulatory, economic, environmental, temporal
4. **CITATIONS_AND_REFERENCES** - Papers, standards, datasets, code repositories
5. **RESOURCES** - Software, hardware, facilities, funding
6. **PROBLEM_DEFINITION** - Failures, gaps, impact assessments
7. **REQUIREMENTS** - Functional, performance, compatibility criteria
8. **TRADE_OFFS** - Competing objectives, technical tensions
9. **RELATIONSHIPS** - Causal links, dependencies, domain bridges
10. **SOLUTION_SPACE** - Proposed approaches, research directions

## ⚙️ Model Selection

### For Research Extraction
```
Model: gemini-2.5-pro
Extraction Passes: 5
Max Workers: 30
Buffer: 10000
```

**Why?** Better context understanding, surfaces implicit information, maintains semantic connections.

### For General Extraction
```
Model: gemini-2.5-flash
Extraction Passes: 2-3
Max Workers: 10-20
Buffer: 8000
```

**Why?** Fast, cost-effective, good for high-volume extraction.

## 🔍 Example JSON Format

```json
{
  "text": "Your source text here...",
  "extractions": [
    {
      "extraction_class": "CONSTRAINTS",
      "extraction_text": "minimum linewidth ≥100nm",
      "attributes": {
        "category": "CONSTRAINTS",
        "subcategory": "physical_constraints",
        "element_name": "minimum_linewidth",
        "attribute_value": "≥100nm",
        "constraint_type": "geometric",
        "constraint_source": "TSMC foundry",
        "constraint_enforcement": "automatic_DRC_check",
        "confidence_level": "certain",
        "impact_score": "10",
        "source_context": "requires minimum linewidth ≥100nm for TSMC fabrication",
        "related_to": "density_based_topology,TSMC_process",
        "notes": "Hard constraint. Non-negotiable."
      }
    }
  ]
}
```

## 🛠️ Local Development

```bash
# Install
pip install -r requirements.txt

# Set API key
export LANGEXTRACT_API_KEY="your-key"

# Run server
fastmcp run server.py

# Test in another terminal
fastmcp client server.py
```

## 📁 Output Files

### CSV Output
- **File**: `output/research_context.csv`
- **Format**: 30 columns with headers
- **Encoding**: UTF-8
- **Use**: Excel, Pandas, database import

### JSONL Output
- **File**: `output/extraction_results.jsonl`
- **Format**: One JSON object per line
- **Use**: Streaming processing, LangExtract tools

### HTML Visualization
- **File**: `output/visualization.html`
- **Format**: Interactive highlighting
- **Use**: Review extractions in context

## 🔗 Links

- **LangExtract**: [https://github.com/google/langextract](https://github.com/google/langextract)
- **FastMCP**: [https://gofastmcp.com](https://gofastmcp.com)
- **Gemini API**: [https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
- **Get API Key**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

## ❓ Troubleshooting

### Server not responding?
- Check FastMCP Cloud logs
- Verify `LANGEXTRACT_API_KEY` is set
- Ensure server file is `server.py`

### Claude can't connect?
- Verify URL in config is correct (must start with https://)
- Restart Claude Desktop after config changes
- Check config JSON syntax is valid

### Extraction errors?
- Verify API key is valid
- Check examples are formatted correctly
- Use `get_research_examples` for proper format

### CSV export fails?
- Ensure `pandas` is installed
- Check `output/` directory exists
- Verify result_id is valid with `list_stored_results`

## 📝 Citation

If you use this tool for research, please cite:

```bibtex
@software{langextract_research_mcp,
  title={LangExtract MCP Server - Research Context Extraction},
  author={Your Name},
  year={2025},
  url={https://github.com/jsagir/langextract-mcp-server}
}
```

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests if applicable
4. Submit a pull request

## 🎯 Roadmap

- [ ] Add support for PDF direct extraction
- [ ] Implement graph database export (Neo4j)
- [ ] Add citation network visualization
- [ ] Support for multi-document synthesis
- [ ] Integration with reference managers (Zotero, Mendeley)
- [ ] Advanced relationship inference
- [ ] Custom ontology support

---

**Made with ❤️ for researchers who need comprehensive context extraction**
