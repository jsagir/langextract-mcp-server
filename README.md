# LangExtract MCP Server 🚀

MCP server for structured data extraction using LangExtract and Gemini AI.

## 🎯 Features

8 powerful extraction tools:
- extract_structured_data - Main extraction
- extract_from_url - Extract from URLs
- save_results_to_jsonl - Save results
- generate_visualization - Create HTML viz
- list_stored_results - List all results
- get_extraction_details - Get details
- create_example_template - Make templates
- get_supported_models - List models

## 🚀 Deploy

1. Push to GitHub
2. Go to https://fastmcp.com/dashboard
3. Connect repository
4. Set LANGEXTRACT_API_KEY
5. Deploy!

## 🔑 Get API Key

https://aistudio.google.com/app/apikey

## ⚙️ Claude Config

Location: %APPDATA%\Claude\claude_desktop_config.json

```json
{
  "mcpServers": {
    "langextract": {
      "url": "https://your-deployment.fastmcp.com"
    }
  }
}
```

## 📝 Example

> "Use langextract to extract people and dates from: Dr. Smith found X on Jan 1, 2024"

## 📄 License

Apache 2.0
