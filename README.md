# 🔍 LangExtract MCP Server

MCP server for structured data extraction using LangExtract and Gemini AI.

## 🎯 Features

**8 Powerful Tools:**
- `extract_structured_data` - Main extraction from text
- `extract_from_url` - Extract directly from URLs  
- `save_results_to_jsonl` - Save results to JSONL format
- `generate_visualization` - Create interactive HTML visualization
- `list_stored_results` - List all extraction results
- `get_extraction_details` - Get detailed extraction info
- `create_example_template` - Generate example templates
- `get_supported_models` - List available models

## 🚀 Deploy to FastMCP Cloud

### 1. Get Gemini API Key
Visit: https://aistudio.google.com/app/apikey

Click "Create API key" and copy it.

### 2. Deploy on FastMCP
1. Go to https://fastmcp.com/dashboard
2. Sign in with GitHub
3. Click "Create New Project"
4. Select this repository
5. Configure:
   - **Server File**: `server.py`
   - **Environment Variable**: 
     - Name: `LANGEXTRACT_API_KEY`
     - Value: (paste your Gemini API key)
6. Click "Deploy"
7. Copy your deployment URL: `https://your-project.fastmcp.cloud`

### 3. Configure Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add this:
```json
{
  "mcpServers": {
    "langextract": {
      "url": "https://your-project.fastmcp.cloud"
    }
  }
}
```

Replace `your-project.fastmcp.cloud` with your actual URL.

**Restart Claude Desktop** after saving.

## 💡 Quick Usage Example

In Claude Desktop, try:

```
Extract people and medications from this text:
"Dr. Sarah Johnson prescribed 50mg aspirin to patient John Doe."

Use extract_structured_data with examples:
- Person: "Dr. Smith" with role="doctor"
- Medication: "aspirin" with dosage="50mg"
```

## 📊 Example Format

```json
{
  "text": "Dr. Smith prescribed 50mg aspirin.",
  "extractions": [
    {
      "extraction_class": "person",
      "extraction_text": "Dr. Smith",
      "attributes": {"role": "doctor"}
    },
    {
      "extraction_class": "medication",
      "extraction_text": "aspirin",
      "attributes": {"dosage": "50mg"}
    }
  ]
}
```

## 🔧 Advanced Parameters

### Higher Recall (More Accurate)
```python
extraction_passes=3
max_workers=10
max_char_buffer=2000
```

### Faster Processing
```python
extraction_passes=1
max_workers=20
max_char_buffer=8000
```

## 🏠 Local Development

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

## 📚 Resources

- **LangExtract**: https://github.com/google/langextract
- **FastMCP**: https://gofastmcp.com
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **Get API Key**: https://aistudio.google.com/app/apikey

## 🐛 Troubleshooting

**Server not responding?**
- Check FastMCP Cloud logs
- Verify `LANGEXTRACT_API_KEY` is set
- Ensure server file is `server.py`

**Claude can't connect?**
- Verify URL in config is correct (must start with https://)
- Restart Claude Desktop after config changes
- Check config JSON syntax is valid

**Extraction errors?**
- Verify API key is valid
- Check examples are formatted correctly
- Use `create_example_template` for help

## 📄 License

MIT
