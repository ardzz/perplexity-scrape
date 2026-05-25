# CLI Usage Guide

## Interactive CLI (`cli.py`)

Antarmuka terminal interaktif untuk Perplexity AI dengan multi-turn history, streaming, dan MCP tool integration.

### Setup

1. Clone repo dan install dependencies:
   ```bash
   git clone https://github.com/ardzz/perplexity-scrape.git
   cd perplexity-scrape
   pip install -r requirements.txt
   ```

2. Copy `.env.example` dan isi credential Perplexity:
   ```bash
   cp .env.example .env
   # Edit .env dan isi PERPLEXITY_SESSION_TOKEN, dll
   ```

### Menjalankan CLI

```bash
# Mode default (claude46sonnetthinking)
python3 cli.py

# Pilih model spesifik
python3 cli.py --model sonar-pro
python3 cli.py --model claude46sonnetthinking

# Dengan MCP tools (BurpSuite, dll)
python3 cli.py --mcp ./mcp_tools.json

# Load sesi sebelumnya
python3 cli.py --load ~/.perplexity_cli/sessions/session_20240525.json

# Mode incognito (tidak muncul di dashboard Perplexity)
python3 cli.py --incognito

# System prompt kustom
python3 cli.py --system "Kamu adalah security researcher. Fokus ke vulnerability analysis."

# Kombinasi lengkap
python3 cli.py --model claude46sonnetthinking --mcp ./mcp_tools.json --incognito
```

### Slash Commands

| Command | Fungsi |
|---|---|
| `/model <nama>` | Ganti model aktif |
| `/models` | List semua model yang tersedia |
| `/clear` | Hapus history percakapan sesi ini |
| `/save [path]` | Simpan sesi ke file JSON |
| `/load <path>` | Load sesi dari file JSON |
| `/sessions` | List sesi tersimpan |
| `/system <teks>` | Set system prompt |
| `/system` | Tampilkan system prompt aktif |
| `/mode <nama>` | Ganti mode: `copilot`, `search`, `reasoning`, `writing` |
| `/focus <nama>` | Ganti fokus: `internet`, `academic`, `wolfram`, `youtube`, `reddit` |
| `/incognito` | Toggle incognito mode |
| `/tools` | List semua MCP tools yang terhubung |
| `/tool <nama> [args]` | Panggil MCP tool secara manual |
| `/mcp <config.json>` | Connect ke MCP servers dari config file |
| `/history` | Tampilkan riwayat percakapan |
| `/status` | Info sesi aktif |
| `/help` | Bantuan |
| `exit` / `quit` | Keluar |

### MCP Tool Integration

Buat file `mcp_tools.json` (lihat `mcp_tools.example.json`):

```json
{
  "mcpServers": {
    "burpsuite": {
      "command": "python",
      "args": ["/path/to/burpsuite-mcp/server.py"],
      "env": {
        "BURP_API_KEY": "your-key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    }
  }
}
```

Jalankan dengan MCP:
```bash
python3 cli.py --mcp ./mcp_tools.json
```

Saat ada tools terhubung, LLM bisa call tools dengan format:
```
TOOL_CALL: burpsuite.active_scan {"url": "https://target.com", "type": "xss"}
```
CLI akan otomatis mengeksekusi dan mengembalikan hasil ke konteks percakapan.

Atau panggil manual:
```
/tool burpsuite.active_scan url=https://target.com type=xss
```

### Model yang Tersedia

- `claude46sonnetthinking` (default)
- `claude45sonnetthinking`
- `claude37sonnetthinking`
- `claude35sonnet`
- `sonar-pro`
- `sonar`
- `sonar-reasoning-pro`
- `sonar-reasoning`
- `r1-1776`
- `gpt-4o`
- `o3-mini`
- `gemini-2.0-flash`

### Session Management

Sesi disimpan otomatis di `~/.perplexity_cli/sessions/` saat keluar.

List sesi:
```bash
# Via CLI
/sessions

# Atau langsung
ls ~/.perplexity_cli/sessions/
```

Load sesi lama:
```bash
python3 cli.py --load ~/.perplexity_cli/sessions/session_20240525_143022.json
```
