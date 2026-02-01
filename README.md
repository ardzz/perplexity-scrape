# Perplexity Scrape

[![Tests](https://img.shields.io/github/actions/workflow/status/ardzz/perplexity-scrape/tests.yml?branch=master&style=flat-square&label=tests)](https://github.com/ardzz/perplexity-scrape/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/ardzz/perplexity-scrape?style=flat-square&logo=codecov)](https://codecov.io/gh/ardzz/perplexity-scrape)
[![GitHub Stars](https://img.shields.io/github/stars/ardzz/perplexity-scrape?style=flat-square)](https://github.com/ardzz/perplexity-scrape/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ardzz/perplexity-scrape?style=flat-square)](https://github.com/ardzz/perplexity-scrape/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?style=flat-square&logo=docker)](https://ghcr.io/ardzz/perplexity-scrape)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg?style=flat-square)](https://modelcontextprotocol.io/)

> **Access premium AI models (Claude, GPT, Gemini, Grok) through Perplexity AI** — as an MCP server for AI assistants or an OpenAI-compatible REST API for any application.

Transform your Perplexity Pro subscription into a powerful API backend. Use cutting-edge AI models like Claude 4.5 Sonnet, GPT-5.2, Gemini 3, and Grok 4.1 through a single unified interface — no separate API keys needed.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Setup](#setup)
- [MCP Server](#mcp-server)
  - [Run Modes](#run-mcp-server-stdio-mode---default)
  - [Client Configuration](#mcp-client-configuration)
  - [HTTP Examples](#mcp-http-examples)
  - [Available Tools](#available-mcp-tools)
  - [Research Categories](#research-categories)
- [OpenAI-Compatible REST API](#openai-compatible-rest-api)
  - [Endpoints](#endpoints)
  - [Examples](#curl-example)
- [Combined Server](#combined-server-rest-api--mcp)
- [Docker Deployment](#docker-deployment)
  - [Available Images](#available-images)
  - [Docker Compose](#docker-compose)
  - [Deployment Platforms](#deployment-platforms)
- [Authentication](#authentication)
- [Available Models](#available-models)
- [Environment Variables](#environment-variables)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **MCP Server** | 6 specialized search tools for AI assistants (Claude Desktop, OpenCode, etc.) |
| **REST API** | OpenAI-compatible `/v1/chat/completions` endpoint — drop-in replacement |
| **Multi-Model** | Access Claude, GPT, Gemini, Grok, Kimi through a single Perplexity account |
| **Web Search** | Real-time internet search with citations and sources |
| **Academic Search** | Scholarly sources from academic databases |
| **Docker Ready** | Pre-built images on GitHub Container Registry |
| **Optional Auth** | Protect endpoints with API key authentication |

---

## Quick Start

**Docker (recommended):**
```bash
docker run -d -p 8045:8045 \
  -e PERPLEXITY_SESSION_TOKEN=your_token \
  -e PERPLEXITY_CF_CLEARANCE=your_clearance \
  -e PERPLEXITY_VISITOR_ID=your_visitor_id \
  -e PERPLEXITY_SESSION_ID=your_session_id \
  ghcr.io/ardzz/perplexity-scrape:latest
```

**Local:**
```bash
pip install -r requirements.txt
python unified_service.py
```

Then use the API:
```bash
curl http://localhost:8045/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-4.5-sonnet-thinking", "messages": [{"role": "user", "content": "Hello!"}]}'
```

---

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure `.env` file** with your Perplexity credentials:
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

The `perplexity_research` tool supports 20 specialized categories organized into three groups:

#### Programming Categories

| Category | Best For |
|----------|----------|
| `api` | API/SDK documentation and usage patterns |
| `library` | Library/framework guides and integration |
| `implementation` | Step-by-step implementation guidance |
| `debugging` | Troubleshooting and debugging approaches |
| `comparison` | Technical comparisons between options |
| `general` | General programming research (default) |

#### ML Core Categories

| Category | Best For |
|----------|----------|
| `ml_architecture` | Neural network architectures and design patterns |
| `ml_training` | Training optimization, hyperparameters, convergence |
| `ml_concepts` | ML/DL theoretical concepts and foundations |
| `ml_frameworks` | PyTorch, TensorFlow, JAX framework usage |
| `ml_math` | Mathematical foundations (linear algebra, calculus, probability) |
| `ml_paper` | Research paper analysis and implementation |
| `ml_debugging` | ML model debugging, loss issues, gradient problems |

#### ML Dataset Categories

| Category | Best For |
|----------|----------|
| `ml_dataset_tabular` | Structured/tabular data (CSV, databases, feature engineering) |
| `ml_dataset_image` | Image datasets (classification, detection, segmentation) |
| `ml_dataset_text` | Text/NLP datasets (classification, NER, generation) |
| `ml_dataset_timeseries` | Time series data (forecasting, anomaly detection) |
| `ml_dataset_audio` | Audio datasets (speech, music, sound classification) |
| `ml_dataset_graph` | Graph-structured data (social networks, molecules) |
| `ml_dataset_multimodal` | Multi-modal datasets (image+text, video+audio) |

**Examples:**
```python
# Programming research
perplexity_research(topic="FastAPI authentication", category="implementation")

# ML framework research
perplexity_research(topic="PyTorch DataLoader optimization", category="ml_frameworks")

# ML dataset research
perplexity_research(topic="CIFAR-10 image classification", category="ml_dataset_image")
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

## Docker Deployment

Pre-built Docker images are available on GitHub Container Registry.

### Available Images

| Image | Description | Port |
|-------|-------------|------|
| `ghcr.io/ardzz/perplexity-scrape` | Combined server (REST API + MCP) | 8045 |
| `ghcr.io/ardzz/perplexity-openai` | REST API only | 8045 |
| `ghcr.io/ardzz/perplexity-mcp` | MCP HTTP server only | 8000 |

### Quick Start with Docker

```bash
docker run -d \
  --name perplexity \
  -p 8045:8045 \
  -e PERPLEXITY_SESSION_TOKEN=your_session_token \
  -e PERPLEXITY_CF_CLEARANCE=your_cf_clearance \
  -e PERPLEXITY_VISITOR_ID=your_visitor_id \
  -e PERPLEXITY_SESSION_ID=your_session_id \
  -e API_KEY=your-api-key \
  ghcr.io/ardzz/perplexity-scrape:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  perplexity:
    image: ghcr.io/ardzz/perplexity-scrape:latest
    container_name: perplexity
    restart: unless-stopped
    ports:
      - "8045:8045"
    environment:
      # Perplexity credentials (required)
      - PERPLEXITY_SESSION_TOKEN=your_session_token
      - PERPLEXITY_CF_CLEARANCE=your_cf_clearance
      - PERPLEXITY_VISITOR_ID=your_visitor_id
      - PERPLEXITY_SESSION_ID=your_session_id
      # Optional settings
      - API_KEY=your-api-key
      - DEFAULT_MODEL=claude45sonnetthinking
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8045/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Building from Source

```bash
# Combined server (recommended)
docker build -f docker/Dockerfile.combined -t perplexity-scrape .

# REST API only
docker build -f docker/Dockerfile.openai -t perplexity-openai .

# MCP server only
docker build -f docker/Dockerfile.mcp -t perplexity-mcp .
```

### Deployment Platforms

The Docker images work with any container platform:

- **Coolify** - Set environment variables in the deployment settings
- **Railway** - Use the Docker image URL directly
- **Fly.io** - Deploy with `fly launch --image ghcr.io/ardzz/perplexity-scrape`
- **DigitalOcean App Platform** - Use container registry image
- **AWS ECS / Google Cloud Run / Azure Container Apps** - Standard container deployment

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
| `PERPLEXITY_SESSION_TOKEN` | *(required)* | Session token from Perplexity cookies |
| `PERPLEXITY_CF_CLEARANCE` | *(required)* | Cloudflare clearance token |
| `PERPLEXITY_VISITOR_ID` | *(required)* | Visitor ID from Perplexity |
| `PERPLEXITY_SESSION_ID` | *(required)* | Session ID from Perplexity |
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
