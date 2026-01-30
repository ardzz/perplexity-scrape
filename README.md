# Perplexity MCP Server

An MCP server and OpenAI-compatible REST API that provides Perplexity AI search capabilities.

## Features

- **MCP Server**: 6 specialized search tools for AI assistants
- **REST API**: OpenAI-compatible `/v1/chat/completions` endpoint
- **Multi-Model**: Access Claude, GPT, Gemini, Grok, Kimi through Perplexity

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

---

## MCP Server

### Run MCP Server

```bash
python server.py
```

### MCP Configuration

Add to your MCP config:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "python",
      "args": ["/path/to/perplexity-mcp/server.py"],
      "env": {}
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `perplexity_ask` | Full search with mode, model, and focus options |
| `perplexity_quick_search` | Quick search returning just the answer text |
| `perplexity_academic_search` | Search academic/scholarly sources |
| `perplexity_comprehensive_search` | Search both web and academic sources |
| `perplexity_research` | Programming-focused research with category-specific prompts |
| `perplexity_general_research` | General/academic research on any topic |

### Research Categories

The `perplexity_research` tool supports 6 specialized categories:

| Category | Best For |
|----------|----------|
| `api` | API/SDK documentation and usage patterns |
| `library` | Library/framework guides and integration |
| `implementation` | Step-by-step implementation guidance |
| `debugging` | Troubleshooting and debugging approaches |
| `comparison` | Technical comparisons between options |
| `general` | General programming research (default) |

**Example:**
```python
perplexity_research(topic="FastAPI authentication", category="implementation")
```

---

## OpenAI-Compatible REST API

### Run REST Server

```bash
python rest_server.py
```

Default: `http://127.0.0.1:8045`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/chat/completions` | Create chat completion (OpenAI-compatible) |
| GET | `/v1/models` | List available models |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI documentation |

### cURL Example

```bash
curl -X POST http://127.0.0.1:8045/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-4.5-sonnet-thinking",
    "messages": [
      {"role": "user", "content": "What is quantum computing?"}
    ]
  }'
```

### Python Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8045/v1",
    api_key="not-needed"  # Authentication via Perplexity cookies
)

response = client.chat.completions.create(
    model="claude-4.5-sonnet-thinking",
    messages=[
        {"role": "user", "content": "Explain machine learning"}
    ]
)
print(response.choices[0].message.content)
```

---

## Available Models

### Perplexity Native
| Model ID | Description |
|----------|-------------|
| `sonar` | Perplexity Sonar (experimental) |
| `pplx-alpha` | Perplexity Alpha - faster responses |

### Claude (Anthropic)
| Model ID | Description |
|----------|-------------|
| `claude-4.5-sonnet` | Claude 4.5 Sonnet |
| `claude-4.5-sonnet-thinking` | Claude 4.5 Sonnet with Reasoning **(default)** |
| `claude-4.5-opus` | Claude 4.5 Opus |
| `claude-4.5-opus-thinking` | Claude 4.5 Opus with Reasoning |

### Gemini (Google)
| Model ID | Description |
|----------|-------------|
| `gemini-3-flash` | Gemini 3 Flash |
| `gemini-3-flash-thinking` | Gemini 3 Flash with Reasoning |
| `gemini-3-pro` | Gemini 3 Pro with Reasoning |

### GPT (OpenAI)
| Model ID | Description |
|----------|-------------|
| `gpt-5.2` | GPT 5.2 |
| `gpt-5.2-thinking` | GPT 5.2 with Reasoning |

### Grok (xAI)
| Model ID | Description |
|----------|-------------|
| `grok-4.1` | Grok 4.1 |
| `grok-4.1-thinking` | Grok 4.1 with Reasoning |

### Kimi (Moonshot)
| Model ID | Description |
|----------|-------------|
| `kimi-k2-thinking` | Kimi K2 with Reasoning |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REST_API_HOST` | `127.0.0.1` | REST API host |
| `REST_API_PORT` | `8045` | REST API port |
| `DEFAULT_MODEL` | `claude45sonnetthinking` | Default model for requests |
| `DEFAULT_MODE` | `copilot` | Search mode (copilot/search) |
| `DEFAULT_SEARCH_FOCUS` | `internet` | Search focus (internet/academic) |

---

## Architecture

```
perplexity-mcp/
├── server.py              # MCP server entry point
├── rest_server.py         # FastAPI REST server entry point
├── perplexity_client.py   # Core Perplexity API client
├── src/
│   ├── api/
│   │   ├── routes.py          # REST API endpoints
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   └── error_handlers.py  # Error handling
│   ├── models/
│   │   ├── model_mapping.py   # OpenAI → Perplexity model mapping
│   │   ├── openai_models.py   # OpenAI-compatible request/response models
│   │   └── perplexity_models.py
│   ├── services/
│   │   ├── chat_completion_service.py
│   │   ├── perplexity_adapter.py
│   │   └── stream_formatter.py
│   ├── config.py          # Configuration management
│   └── utils/
└── test_client.py         # Test client for wrapper
```

---

## License

MIT
