# Complete Research Context Extraction Workflow

## 🎯 Workflow Overview

```
Input Text → extract_research_context → export_to_research_csv → CSV File
                                       ↓
                                  Analysis & Queries
```

## 📝 Step-by-Step Guide

### Step 1: Prepare Your Research Text

Collect your research material:
- Paper abstracts
- Technical documentation
- Research proposals
- Literature reviews
- Patent applications
- Technical reports

**Best practices:**
- Include complete sentences
- Keep paragraphs together (don't fragment)
- Include citations in original format
- Preserve technical terms exactly

### Step 2: Extract Research Context

#### In Claude Desktop:

```
Extract complete research context from this text:

[Paste your research text here]

Use extract_research_context with:
- model: gemini-2.5-pro
- extraction_passes: 5
```

#### What happens:
1. Text analyzed with 5 specialized examples
2. All 10 categories extracted simultaneously
3. Relationships automatically linked
4. Source context preserved
5. Implicit assumptions surfaced

#### Expected output:
```json
{
  "success": true,
  "result_id": "abc123...",
  "total_extractions": 47,
  "category_breakdown": {
    "CITATIONS_AND_REFERENCES": 8,
    "CURRENT_APPROACHES": 12,
    "CONSTRAINTS": 15,
    "DOMAIN_CONTEXT": 6,
    "PROBLEM_DEFINITION": 4,
    "REQUIREMENTS": 2
  }
}
```

### Step 3: Export to CSV

```
Export the results to CSV:

Use export_to_research_csv with:
- result_id: [the ID from step 2]
- output_name: "my_research_context.csv"
```

#### Output file structure:
```
output/my_research_context.csv

Columns (30):
id, category, subcategory, element_name, relationship_type,
relationship_target, attribute_key, attribute_value, evidence_type,
confidence_level, temporal_marker, impact_score, citation_key,
citation_url, citation_authors, citation_year, citation_type,
resource_name, resource_url, resource_type, domain_hierarchy,
domain_level, parent_domain, child_domains, cross_domain_refs,
constraint_type, constraint_source, constraint_enforcement,
constraint_dependencies, source_context, related_to, notes
```

### Step 4: Analyze the CSV

#### Load in Python (Pandas)

```python
import pandas as pd

# Load the CSV
df = pd.read_csv('output/my_research_context.csv')

# View summary
print(f"Total extractions: {len(df)}")
print(f"Categories: {df['category'].unique()}")

# Filter by category
constraints = df[df['category'] == 'CONSTRAINTS']
citations = df[df['category'] == 'CITATIONS_AND_REFERENCES']

# View high-impact items
high_impact = df[df['impact_score'].astype(str).str.isdigit()]
high_impact = high_impact[high_impact['impact_score'].astype(int) >= 8]

# Trace relationships
def get_related(element_name):
    """Find all items related to this element"""
    related_ids = df[df['element_name'] == element_name]['relationship_target'].iloc[0]
    if pd.isna(related_ids) or related_ids == '':
        return pd.DataFrame()
    ids = [int(x) for x in related_ids.split(',') if x.strip()]
    return df[df['id'].isin(ids)]

# Example: Find everything related to a specific method
related = get_related('density_based_topology')
print(related[['id', 'element_name', 'category', 'source_context']])
```

#### Query Examples

**1. Find all hard constraints:**
```python
hard_constraints = df[
    (df['category'] == 'CONSTRAINTS') & 
    (df['notes'].str.contains('non-negotiable|hard', case=False, na=False))
]
```

**2. Get complete citation network:**
```python
citations = df[df['category'] == 'CITATIONS_AND_REFERENCES']
citation_network = citations[['citation_key', 'citation_authors', 'citation_year', 'related_to']]
```

**3. Find cross-domain connections:**
```python
interdisciplinary = df[df['cross_domain_refs'].notna()]
```

**4. Identify implicit constraints:**
```python
implicit = df[
    (df['category'] == 'CONSTRAINTS') & 
    (df['notes'].str.contains('implicit|unstated', case=False, na=False))
]
```

**5. Build problem-solution map:**
```python
problems = df[df['category'] == 'PROBLEM_DEFINITION']
requirements = df[df['category'] == 'REQUIREMENTS']

# Link them
for _, prob in problems.iterrows():
    related_req_ids = prob['relationship_target']
    if pd.notna(related_req_ids):
        req = requirements[requirements['id'].isin([int(x) for x in str(related_req_ids).split(',')])]
        print(f"Problem: {prob['element_name']}")
        print(f"  → Requirements: {req['element_name'].tolist()}")
```

### Step 5: Visualize (Optional)

```
Generate visualization for result:

Use generate_visualization with:
- result_id: [your result ID]
- output_name: "research_viz.html"
```

Open `output/research_viz.html` in browser to see:
- Highlighted extractions in original text
- Color-coded by category
- Hover to see attributes
- Click to see relationships

## 🔄 Advanced Workflows

### Multi-Document Synthesis

Extract from multiple papers and combine:

```python
import pandas as pd
import glob

# Extract from each paper (repeat Step 2-3 for each)
# Then combine CSVs

all_csvs = glob.glob('output/paper_*.csv')
combined = pd.concat([pd.read_csv(f) for f in all_csvs], ignore_index=True)

# Deduplicate by element_name
combined = combined.drop_duplicates(subset=['element_name', 'category'])

# Rebuild relationship graph
# (You'll need to resolve cross-file references)

combined.to_csv('output/combined_research_context.csv', index=False)
```

### Export to Knowledge Graph

```python
# Example: Neo4j Cypher export
def generate_cypher(df):
    """Generate Cypher statements for Neo4j import"""
    
    cypher = []
    
    # Create nodes
    for _, row in df.iterrows():
        props = {
            'element_name': row['element_name'],
            'category': row['category'],
            'source_context': row['source_context'],
            'confidence': row['confidence_level']
        }
        cypher.append(
            f"CREATE (n{row['id']}:{row['category']} {props})"
        )
    
    # Create relationships
    for _, row in df.iterrows():
        if pd.notna(row['relationship_target']) and row['relationship_target']:
            targets = [int(x) for x in str(row['relationship_target']).split(',')]
            for target in targets:
                cypher.append(
                    f"MATCH (a), (b) WHERE id(a)={row['id']} AND id(b)={target} "
                    f"CREATE (a)-[:{row['relationship_type'] or 'RELATES_TO'}]->(b)"
                )
    
    return '\n'.join(cypher)

# Generate and save
cypher_script = generate_cypher(df)
with open('output/import_neo4j.cypher', 'w') as f:
    f.write(cypher_script)
```

### Integration with Reference Managers

Export citations to BibTeX:

```python
def export_bibtex(df):
    """Export citations to BibTeX format"""
    
    citations = df[df['category'] == 'CITATIONS_AND_REFERENCES']
    bibtex = []
    
    for _, row in citations.iterrows():
        if row['citation_type'] == 'journal_article':
            entry = f"""@article{{{row['citation_key']},
    author = {{{row['citation_authors'].replace(',', ' and ')}}},
    year = {{{row['citation_year']}}},
    title = {{{row['element_name']}}},
    doi = {{{row['citation_url'].replace('https://doi.org/', '')}}}
}}"""
            bibtex.append(entry)
    
    return '\n\n'.join(bibtex)

# Export
bibtex_content = export_bibtex(df)
with open('output/references.bib', 'w') as f:
    f.write(bibtex_content)
```

## 📊 Example Analyses

### Analysis 1: Constraint Network

Find all constraints and their dependencies:

```python
import networkx as nx
import matplotlib.pyplot as plt

# Build constraint dependency graph
constraints = df[df['category'] == 'CONSTRAINTS']
G = nx.DiGraph()

for _, row in constraints.iterrows():
    G.add_node(row['element_name'], 
               type=row['constraint_type'],
               source=row['constraint_source'])
    
    if pd.notna(row['constraint_dependencies']):
        deps = [d.strip() for d in str(row['constraint_dependencies']).split(',')]
        for dep in deps:
            G.add_edge(dep, row['element_name'])

# Visualize
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=2000, font_size=8, arrows=True)
plt.title('Constraint Dependency Network')
plt.savefig('output/constraint_network.png')
```

### Analysis 2: Citation Impact

Analyze citation network and influence:

```python
# Count citations
citations = df[df['category'] == 'CITATIONS_AND_REFERENCES']
citation_counts = {}

for _, row in df.iterrows():
    if pd.notna(row['citation_key']) and row['citation_key']:
        citation_counts[row['citation_key']] = citation_counts.get(row['citation_key'], 0) + 1

# Sort by impact
sorted_citations = sorted(citation_counts.items(), key=lambda x: x[1], reverse=True)

print("Most cited papers in this research:")
for cite_key, count in sorted_citations[:10]:
    cite_row = citations[citations['citation_key'] == cite_key].iloc[0]
    print(f"{cite_key} ({cite_row['citation_year']}): {count} mentions")
    print(f"  Authors: {cite_row['citation_authors']}")
    print(f"  URL: {cite_row['citation_url']}\n")
```

### Analysis 3: Gap Analysis Report

Generate a comprehensive gap analysis:

```python
def generate_gap_report(df):
    """Create a structured gap analysis report"""
    
    report = []
    report.append("# Research Gap Analysis\n")
    
    # 1. Identified Problems
    problems = df[df['subcategory'] == 'failure_modes']
    if not problems.empty:
        report.append("## Identified Problems\n")
        for _, prob in problems.iterrows():
            report.append(f"### {prob['element_name']}")
            report.append(f"**Context**: {prob['source_context']}")
            report.append(f"**Impact Score**: {prob['impact_score']}")
            report.append(f"**Notes**: {prob['notes']}\n")
    
    # 2. Current Gaps
    gaps = df[df['subcategory'] == 'gap_analysis']
    if not gaps.empty:
        report.append("## Current Gaps\n")
        for _, gap in gaps.iterrows():
            report.append(f"### {gap['element_name']}")
            report.append(f"**Delta**: {gap['attribute_value']}")
            report.append(f"**Context**: {gap['source_context']}\n")
    
    # 3. Requirements to Address Gaps
    requirements = df[df['category'] == 'REQUIREMENTS']
    if not requirements.empty:
        report.append("## Requirements to Address Gaps\n")
        for _, req in requirements.iterrows():
            report.append(f"- **{req['element_name']}**: {req['attribute_value']}")
            report.append(f"  - Context: {req['source_context']}\n")
    
    # 4. Constraints to Consider
    constraints = df[
        (df['category'] == 'CONSTRAINTS') & 
        (df['impact_score'].astype(str).str.isdigit())
    ]
    constraints = constraints[constraints['impact_score'].astype(int) >= 8]
    if not constraints.empty:
        report.append("## Critical Constraints\n")
        for _, cons in constraints.iterrows():
            report.append(f"- **{cons['element_name']}**: {cons['attribute_value']}")
            report.append(f"  - Type: {cons['constraint_type']}")
            report.append(f"  - Source: {cons['constraint_source']}")
            report.append(f"  - Enforcement: {cons['constraint_enforcement']}\n")
    
    return '\n'.join(report)

# Generate report
report_content = generate_gap_report(df)
with open('output/gap_analysis.md', 'w') as f:
    f.write(report_content)

print("Gap analysis report saved to output/gap_analysis.md")
```

### Analysis 4: Domain Map

Visualize domain hierarchy and cross-domain connections:

```python
def visualize_domain_map(df):
    """Create domain hierarchy visualization"""
    
    domains = df[df['category'] == 'DOMAIN_CONTEXT']
    
    # Build hierarchy
    hierarchy = {}
    for _, row in domains.iterrows():
        if pd.notna(row['domain_hierarchy']):
            path = row['domain_hierarchy'].split('->')
            current = hierarchy
            for level in path:
                if level not in current:
                    current[level] = {}
                current = current[level]
    
    # Print tree
    def print_tree(tree, indent=0):
        for key, subtree in tree.items():
            print('  ' * indent + f"└─ {key}")
            print_tree(subtree, indent + 1)
    
    print("Domain Hierarchy:")
    print_tree(hierarchy)
    
    # Cross-domain connections
    cross_domain = domains[domains['cross_domain_refs'].notna()]
    if not cross_domain.empty:
        print("\nCross-Domain Connections:")
        for _, row in cross_domain.iterrows():
            print(f"- {row['element_name']}: {row['cross_domain_refs']}")
            print(f"  Context: {row['source_context']}\n")

visualize_domain_map(df)
```

## 🎯 Real-World Example

### Complete workflow for a research paper

```python
# Example: Analyzing a photonics research paper

# Step 1: Text prepared (research paper abstract + methods)
research_text = """
Jensen & Sigmund (2011) introduced topology optimization for photonics 
using density-based methods, which converges well with accurate gradients 
but requires minimum linewidth ≥100nm for TSMC fabrication. Current inverse 
design methods fail to guarantee manufacturability constraints, creating a 
gap between optimized designs and fabricable devices. FDTD simulations using 
Lumerical require HPC clusters (128+ cores) to achieve convergence in 
reasonable time, trading computational cost for accuracy. Devices operating 
at 1550nm wavelength for telecom applications must comply with ITU-T 
standards, implicitly requiring temperature stability from -40°C to 85°C.
"""

# Step 2: Extract (done via Claude)
# Result ID: abc123def456

# Step 3: Load and analyze
df = pd.read_csv('output/photonics_context.csv')

# Quick stats
print(f"Total extractions: {len(df)}")
print(f"Categories: {df['category'].value_counts().to_dict()}")

# Find the core method
methods = df[df['category'] == 'CURRENT_APPROACHES']
print("\nCore Methods:")
for _, m in methods.iterrows():
    print(f"- {m['element_name']}: {m['source_context']}")

# Find all constraints
constraints = df[df['category'] == 'CONSTRAINTS']
print("\nAll Constraints:")
for _, c in constraints.iterrows():
    print(f"- {c['element_name']} ({c['constraint_type']}): {c['attribute_value']}")
    print(f"  Source: {c['constraint_source']}")
    print(f"  Impact: {c['impact_score']}")

# Trace relationships
method = df[df['element_name'] == 'density_based_topology'].iloc[0]
related_ids = [int(x) for x in str(method['relationship_target']).split(',') if x.strip()]
related = df[df['id'].isin(related_ids)]

print(f"\nItems related to 'density_based_topology':")
for _, r in related.iterrows():
    print(f"- {r['element_name']} ({r['category']})")

# Generate gap report
gap_report = generate_gap_report(df)
print("\n" + "="*50)
print(gap_report)
```

### Expected Output:

```
Total extractions: 12
Categories: {
  'CITATIONS_AND_REFERENCES': 2,
  'CURRENT_APPROACHES': 2,
  'CONSTRAINTS': 4,
  'RESOURCES': 2,
  'TRADE_OFFS': 1,
  'PROBLEM_DEFINITION': 1
}

Core Methods:
- density_based_topology: density-based methods, which converges well with accurate gradients
- FDTD_simulation: FDTD simulations using Lumerical

All Constraints:
- minimum_linewidth (geometric): ≥100nm
  Source: TSMC foundry
  Impact: 10
- temperature_stability (environmental): -40°C to 85°C
  Source: ITU_compliance
  Impact: 8
- HPC_requirement (computational): 128+ cores minimum
  Source: Lumerical FDTD
  Impact: 8
- ITU_compliance (regulatory): ITU-T standards
  Source: ITU-T
  Impact: 9

Items related to 'density_based_topology':
- Jensen2011 (CITATIONS_AND_REFERENCES)
- minimum_linewidth (CONSTRAINTS)

==================================================
# Research Gap Analysis

## Identified Problems

### manufacturability_failure
**Context**: Current inverse design methods fail to guarantee manufacturability constraints
**Impact Score**: 10
**Notes**: Critical failure mode affecting all current approaches

## Current Gaps

### design_fab_gap
**Delta**: unmanufacturable outputs
**Context**: creating a gap between optimized designs and fabricable devices
```

## 🔧 Troubleshooting Tips

### Issue: Missing relationships

**Problem**: `relationship_target` is empty even though `related_to` has values

**Solution**: Make sure to run `export_to_research_csv` which performs relationship resolution. The tool automatically converts element names to IDs.

### Issue: Low extraction count

**Problem**: Only getting 5-10 extractions from a long document

**Solutions**:
1. Increase `extraction_passes` to 5 or more
2. Use `gemini-2.5-pro` instead of flash
3. Check that your text has clear sentence boundaries
4. Verify examples are relevant to your domain

### Issue: Missing implicit constraints

**Problem**: Known constraints not being extracted

**Solution**: Add examples that show implicit extraction:
```python
{
    "text": "Devices for telecom must comply with ITU-T standards, implicitly requiring temperature stability.",
    "extractions": [{
        "extraction_class": "CONSTRAINTS",
        "extraction_text": "temperature stability",
        "attributes": {
            "notes": "IMPLICIT requirement derived from standards"
        }
    }]
}
```

### Issue: Source context truncated

**Problem**: `source_context` field is too short

**Solution**: Increase `max_char_buffer` to 10000 or higher

## 📚 Best Practices

### 1. Example Selection
- Include 5-10 examples minimum
- Cover all categories you want to extract
- Show interconnected extractions
- Include implicit information examples

### 2. Text Preparation
- Keep complete sentences together
- Preserve citation formats exactly
- Include section headers when relevant
- Don't pre-process or clean too aggressively

### 3. Model Configuration
| Use Case | Model | Passes | Workers | Buffer |
|----------|-------|--------|---------|--------|
| Research papers | gemini-2.5-pro | 5 | 30 | 10000 |
| Technical docs | gemini-2.5-pro | 3-4 | 20 | 8000 |
| Quick extraction | gemini-2.5-flash | 2 | 15 | 8000 |
| High volume | gemini-2.5-flash | 1 | 10 | 5000 |

### 4. Post-Processing
- Always validate relationship links
- Check for duplicate element_names
- Verify citation completeness
- Review high-impact items manually

### 5. Iterative Refinement
1. Extract with default settings
2. Review results
3. Identify missing categories
4. Add targeted examples
5. Re-extract with refined examples

## 🚀 Next Steps

After successful extraction:

1. **Knowledge Base**: Import CSV into database
2. **Visualization**: Create domain maps and citation networks
3. **Analysis**: Run gap analysis and constraint mapping
4. **Integration**: Connect with reference manager
5. **Synthesis**: Combine multiple papers
6. **Reporting**: Generate automated insights

## 📖 Additional Resources

- [LangExtract Documentation](https://github.com/google/langextract)
- [Gemini API Guide](https://ai.google.dev/gemini-api/docs)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html)

---

**Questions? Issues?** Open an issue on GitHub or check the troubleshooting section.
