# Perplexity MCP Server

An MCP server and OpenAI-compatible REST API that provides Perplexity AI search capabilities.

## Features

- **MCP Server**: 6 specialized search tools for AI assistants
- **REST API**: OpenAI-compatible `/v1/chat/completions` endpoint
- **Multi-Model**: Access Claude, GPT, Gemini, Grok, Kimi through Perplexity
- **Optional Authentication**: Protect endpoints with API key authentication

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

> **Getting Cookies**: Use the [Perplexity Cookies Extension](https://github.com/ardzz/perplexity-cookies) to easily extract these values, or manually copy them from browser DevTools → Network tab → Copy cookies from any Perplexity request.

---

## MCP Server

### Run MCP Server (stdio mode - default)

```bash
python mcp_service.py
```

This runs the MCP server in stdio mode, suitable for integration with MCP clients like Claude Desktop.

### Run MCP Server (HTTP mode)

```bash
MCP_TRANSPORT_MODE=http python mcp_service.py
```

This runs the MCP server with streamable-http transport at `http://127.0.0.1:8000/mcp`, suitable for remote access.

### MCP Client Configuration

#### Claude Desktop (stdio mode)

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "python",
      "args": ["/path/to/perplexity-mcp/mcp_service.py"],
      "env": {}
    }
  }
}
```

#### OpenCode (stdio local mode)

```json
{
  "perplexity": {
    "type": "local",
    "command": "python",
    "args": ["/path/to/perplexity-mcp/mcp_service.py"],
    "enabled": true
  }
}
```

#### OpenCode (remote HTTP mode)

```json
{
  "perplexity": {
    "type": "remote",
    "url": "https://your-server.com/mcp",
    "enabled": true,
    "headers": {
      "X-API-Key": "your-api-key"
    }
  }
}
```

#### Generic MCP Client (HTTP mode)

Connect to `http://127.0.0.1:8000/mcp` (local) or your deployed URL.

### MCP HTTP Examples

**Initialize session:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "X-API-Key: your-api-key" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**List available tools:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "X-API-Key: your-api-key" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

**Call a tool:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "X-API-Key: your-api-key" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "perplexity_quick_search",
      "arguments": {"query": "What is MCP?"}
    }
  }'
```

> **Note**: The `X-API-Key` header is only required when `API_KEY` is set in your `.env` file. The `Mcp-Session-Id` header is returned in the initialize response and must be included in subsequent requests.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `perplexity_ask` | Full search with mode, model, and focus options |
| `perplexity_quick_search` | Quick search with model selection |
| `perplexity_academic_search` | Search academic sources with model selection |
| `perplexity_comprehensive_search` | Search web + academic with model selection |
| `perplexity_research` | Programming-focused research with model selection |
| `perplexity_general_research` | General/academic research with model selection |

> **Model Selection**: All tools support the `model_preference` parameter. Use any model ID from the [Available Models](#available-models) section. Default: `claude45sonnetthinking`.

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
python rest_api_service.py
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
    api_key="not-needed"  # Or your API_KEY if auth enabled
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

## Combined Server (REST API + MCP)

For convenience, you can run both the REST API and MCP HTTP server on the same port using the combined server:

```bash
python unified_service.py
```

This serves:
- **REST API** at `http://127.0.0.1:8045/v1/...`
- **MCP HTTP** at `http://127.0.0.1:8045/mcp`
- **Documentation** at `http://127.0.0.1:8045/docs`

### Combined Server Examples

**REST API (same as standalone):**
```bash
curl http://localhost:8045/v1/models
```

**MCP Initialize:**
```bash
curl -X POST http://localhost:8045/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**MCP List Tools:**
```bash
curl -X POST http://localhost:8045/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

> **Note**: The `Mcp-Session-Id` header is returned in the initialize response and must be included in subsequent requests.

---

## Authentication

API key authentication is **optional** and disabled by default. When enabled, it protects the `/v1/chat/completions` and `/v1/models` endpoints.

### Enable Authentication

1. Generate a secure API key:
```bash
python scripts/generate_api_key.py
```

2. Add the key to your `.env` file:
```env
API_KEY=your-generated-key-here
```

3. Restart the server. All protected endpoints now require the `X-API-Key` header.

### Using Authentication

**cURL:**
```bash
curl -X POST http://127.0.0.1:8045/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"model": "claude-4.5-sonnet", "messages": [{"role": "user", "content": "Hello"}]}'
```

**Python (OpenAI client):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8045/v1",
    api_key="your-api-key",  # Will be sent as Authorization header
    default_headers={"X-API-Key": "your-api-key"}  # Required header
)
```

**Python (httpx):**
```python
import httpx

response = httpx.post(
    "http://127.0.0.1:8045/v1/chat/completions",
    headers={"X-API-Key": "your-api-key"},
    json={"model": "claude-4.5-sonnet", "messages": [...]}
)
```

### Disable Authentication

Set `API_KEY` to empty or remove it from `.env`:
```env
API_KEY=
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
| `kimi-k2.5-thinking` | Kimi K2.5 Thinking |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REST_API_HOST` | `127.0.0.1` | REST API host |
| `REST_API_PORT` | `8045` | REST API port |
| `DEFAULT_MODEL` | `claude45sonnetthinking` | Default model for requests |
| `DEFAULT_MODE` | `copilot` | Search mode (copilot/search) |
| `DEFAULT_SEARCH_FOCUS` | `internet` | Search focus (internet/academic) |
| `API_KEY` | *(empty)* | API key for authentication (empty = auth disabled) |
| `MCP_TRANSPORT_MODE` | `stdio` | MCP transport mode (`stdio` or `http`) |
| `MCP_HTTP_HOST` | `127.0.0.1` | MCP HTTP server host (when mode=http) |
| `MCP_HTTP_PORT` | `8000` | MCP HTTP server port (when mode=http) |
| `MCP_ENABLE_HOST_CHECK` | `false` | Enable DNS rebinding protection for MCP |
| `MCP_ALLOWED_HOSTS` | *(empty)* | Allowed hosts when host check enabled (comma-separated) |

---

## License

MIT
