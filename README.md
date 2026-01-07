# Perplexity MCP Server

An MCP server that provides Perplexity AI search capabilities to AI assistants.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file with your Perplexity credentials:
```env
PERPLEXITY_SESSION_TOKEN=your_session_token
PERPLEXITY_CF_CLEARANCE=your_cf_clearance
PERPLEXITY_VISITOR_ID=your_visitor_id
PERPLEXITY_SESSION_ID=your_session_id
```

> **Note**: Get these values from browser DevTools → Network tab → Copy cookies from any Perplexity request.

## Usage

### Run MCP Server

```bash
python server.py
```

### Test Wrapper Only

```bash
python test_client.py
```

### MCP Configuration

Add to your MCP config:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "python",
      "args": ["d:/PythonProject/perplexity-mcp/server.py"],
      "env": {}
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `perplexity_ask` | Full search with mode, model, and focus options |
| `perplexity_quick_search` | Quick search returning just the answer |
| `perplexity_academic_search` | Search academic/scholarly sources |

## License

MIT
