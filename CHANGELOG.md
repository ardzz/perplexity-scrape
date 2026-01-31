# CHANGELOG


## v0.7.0 (2026-01-31)

### Continuous Integration

- **security**: Add container scanning to release pipeline
  ([`cfeecac`](https://github.com/ardzz/perplexity-scrape/commit/cfeecacf94eba68176d8a25ba1e8c579c793908a))

- **security**: Add DevSecOps pipeline with Semgrep and Trivy
  ([`6ec7dc6`](https://github.com/ardzz/perplexity-scrape/commit/6ec7dc659b3ca30f2d90e9f346056ddc900095ef))

- Add Semgrep SAST scanning with Python security rulesets - Add Trivy filesystem scanning for
  dependency vulnerabilities - Configure SARIF output for GitHub Security Dashboard - Set up weekly
  scheduled scans and PR/push triggers - Include security scan summary in workflow output

- **security**: Add Semgrep and Trivy ignore files
  ([`5ce268c`](https://github.com/ardzz/perplexity-scrape/commit/5ce268c1b08c47fa5306306f44816b3a64d92ef1))

- **security**: Fix Trivy ignorefile param and upgrade CodeQL to v4
  ([`de49bbf`](https://github.com/ardzz/perplexity-scrape/commit/de49bbf8a82c77df963fbdfd98b680a33f400df7))

- **tests**: Add Codecov test results upload
  ([`06e8d53`](https://github.com/ardzz/perplexity-scrape/commit/06e8d5377f2b5502e4ba309afe3dc71efb7b429e))

### Documentation

- Add community documentation, issue templates, and PR template
  ([`d7b7e2d`](https://github.com/ardzz/perplexity-scrape/commit/d7b7e2d8ff70bdb5c4a308a25bdb3f8a7fc51d4c))

- LICENSE: MIT License with ardzz as copyright holder - CODE_OF_CONDUCT.md: Contributor Covenant
  v2.1 - CONTRIBUTING.md: Comprehensive contribution guide - .github/ISSUE_TEMPLATE/bug_report.yml:
  Bug report form - .github/ISSUE_TEMPLATE/feature_request.yml: Feature request form -
  .github/ISSUE_TEMPLATE/config.yml: Issue template configuration -
  .github/PULL_REQUEST_TEMPLATE.md: PR template

### Features

- **mcp**: Add 7 ML/DL research prompt templates
  ([`e5aee36`](https://github.com/ardzz/perplexity-scrape/commit/e5aee3668cac5fd39a66a417638fd296bea178bc))

Add specialized research prompt templates for machine learning and deep learning topics: -
  ml_architecture: Neural network architectures (CNN, Transformer, etc.) - ml_training: Training
  procedures/optimization (Adam, SGD, backprop) - ml_concepts: Core ML concepts (overfitting,
  regularization) - ml_frameworks: Framework implementations (PyTorch, TensorFlow, JAX) - ml_math:
  Mathematical foundations (linear algebra, calculus for ML) - ml_paper: Research paper explanations
  - ml_debugging: ML-specific debugging (vanishing gradients, NaN loss)

Templates follow hybrid format with mathematical rigor (LaTeX notation) + practical code examples +
  exercises, similar to existing math research prompts.


## v0.6.5 (2026-01-30)

### Bug Fixes

- Correct YAML indentation in tests.yml (line 40)
  ([`bf19dc6`](https://github.com/ardzz/perplexity-scrape/commit/bf19dc6e4b248681c19aca4de86e5ef535dd687a))

### Chores

- **release**: 0.6.5
  ([`d7372a3`](https://github.com/ardzz/perplexity-scrape/commit/d7372a3e2a7f28d0c635e0d93ec0d1373d4115e8))


## v0.6.4 (2026-01-30)

### Bug Fixes

- Resolve CI warnings and Docker build errors
  ([`d631c3b`](https://github.com/ardzz/perplexity-scrape/commit/d631c3b610dba4f41d0fc104fc0ea0a98eafed8a))

- Remove obsolete perplexity_client.py from Dockerfiles (moved to src/core/) - Replace deprecated
  on_event with lifespan in rest_api_service.py - Fix test_client_legacy.py to use assert instead of
  return - Add CODECOV_TOKEN and upgrade codecov-action to v5

### Chores

- **release**: 0.6.4
  ([`f1d2498`](https://github.com/ardzz/perplexity-scrape/commit/f1d249867c4e74ad1c962a4e889bebf8397d33b9))


## v0.6.3 (2026-01-30)

### Bug Fixes

- Update stale imports in test files
  ([`0d95122`](https://github.com/ardzz/perplexity-scrape/commit/0d95122ef88548dd06cba031498f749e25f09408))

- Fix rest_server -> rest_api_service imports - Fix server -> mcp_service imports - All 27 existing
  tests now pass

### Chores

- **release**: 0.6.3
  ([`2211f79`](https://github.com/ardzz/perplexity-scrape/commit/2211f79781bed3a70beb655b7077d85c5ba9ca14))

### Documentation

- Add Docker deployment documentation with GHCR images and compose example
  ([`1859d2e`](https://github.com/ardzz/perplexity-scrape/commit/1859d2e081bbaa4908247f770be6d9b31ff2b127))

- Add link to Perplexity Cookies browser extension for easier setup
  ([`a218659`](https://github.com/ardzz/perplexity-scrape/commit/a218659ba0acae6ca682d0fcfb419b755402f496))

- Add OpenCode stdio local mode configuration example
  ([`d6b0b1c`](https://github.com/ardzz/perplexity-scrape/commit/d6b0b1ceefcfc09697f00c5bdb373175152e43cd))

- Enhance README with badges, table of contents, and improved description
  ([`ea27c4f`](https://github.com/ardzz/perplexity-scrape/commit/ea27c4f904737262cade113e1dc25e34aff652cc))

- Add shields.io badges (stars, forks, license, Python, Docker, MCP) - Add comprehensive table of
  contents with anchor links - Add Quick Start section for immediate usage - Improve project
  description highlighting multi-model access - Add Features table for better overview - Add
  required Perplexity env vars to Environment Variables table - Rename title from 'Perplexity MCP
  Server' to 'Perplexity Scrape'

- Update README with new service names, OpenCode config, and MCP security options
  ([`25267de`](https://github.com/ardzz/perplexity-scrape/commit/25267de012858acd324e240fa2384ae19fae65a7))

- Update script names: server.py → mcp_service.py, rest_server.py → rest_api_service.py,
  combined_server.py → unified_service.py - Add OpenCode remote MCP configuration example - Add MCP
  HTTP examples with proper session handling - Document MCP_ENABLE_HOST_CHECK and MCP_ALLOWED_HOSTS
  env vars - Fix Mcp-Session-Id header casing

### Refactoring

- Move perplexity_client.py to src/core/
  ([`120a8e3`](https://github.com/ardzz/perplexity-scrape/commit/120a8e3396e93085961b055b1ea7c2821b8f51fb))

- Move perplexity_client.py to src/core/perplexity_client.py - Move test_client.py to
  tests/test_client_legacy.py - Update all imports to use new path - Clean up root directory (only
  entry point files remain)


## v0.6.2 (2026-01-30)

### Bug Fixes

- **mcp**: Disable host validation by default for proxy compatibility
  ([`5604b10`](https://github.com/ardzz/perplexity-scrape/commit/5604b10481ecfa6c457ddf86e4b175bc78a4a1d9))

- DNS rebinding protection now disabled by default (allows any host) - Set
  MCP_ENABLE_HOST_CHECK=true to enable host validation - When enabled, MCP_ALLOWED_HOSTS configures
  allowed domains - Simplifies deployment behind reverse proxies (Traefik, Caddy, nginx)

### Chores

- **release**: 0.6.2
  ([`dfb9909`](https://github.com/ardzz/perplexity-scrape/commit/dfb9909ff0b272516b45a0a20601bcba1265fcab))


## v0.6.1 (2026-01-30)

### Bug Fixes

- **mcp**: Add TransportSecuritySettings to allow external hosts via MCP_ALLOWED_HOSTS env var
  ([`fd7f586`](https://github.com/ardzz/perplexity-scrape/commit/fd7f58625870a36b0beac4693c92213ffd62ece4))

### Chores

- **release**: 0.6.1
  ([`1c0afb2`](https://github.com/ardzz/perplexity-scrape/commit/1c0afb2c313601bb524294ea54c8d86843009eda))


## v0.6.0 (2026-01-30)

### Chores

- **release**: 0.6.0
  ([`0f77914`](https://github.com/ardzz/perplexity-scrape/commit/0f779149a77826653488c3f95e590ed22461089f))

### Features

- **docker**: Add multi-image build pipeline for MCP, OpenAI, and unified servers
  ([`2c03675`](https://github.com/ardzz/perplexity-scrape/commit/2c0367509bdeffbbc7c23356a38f2de3b357fba7))

- Add docker/Dockerfile.mcp for MCP HTTP server (port 8000) - Add docker/Dockerfile.openai for REST
  API server (port 8045) - Add docker/Dockerfile.combined for unified server (REST + MCP) - Update
  release.yml with matrix strategy to build 3 images: - ghcr.io/ardzz/perplexity-mcp -
  ghcr.io/ardzz/perplexity-openai - ghcr.io/ardzz/perplexity-scrape - Maintain multi-platform
  support (amd64/arm64) - Add per-image GitHub Actions caching

### Refactoring

- Rename server entry points to service-oriented naming
  ([`65c09bb`](https://github.com/ardzz/perplexity-scrape/commit/65c09bbae40bad11ae751e61fa111ade65ddf438))

- server.py → mcp_service.py - rest_server.py → rest_api_service.py - combined_server.py →
  unified_service.py - Updated Dockerfile COPY and CMD to use new names - Updated internal imports
  in unified_service.py


## v0.5.0 (2026-01-30)

### Chores

- **release**: 0.5.0
  ([`c562ddc`](https://github.com/ardzz/perplexity-scrape/commit/c562ddcd51f5c1f41ddb9d02c93642ece3dfe736))

### Features

- **docker**: Switch to combined server for REST API + MCP support
  ([`17187ad`](https://github.com/ardzz/perplexity-scrape/commit/17187ad4aa277bbe9f51c2180565ebc09d4fa206))

- Include combined_server.py and server.py in Docker image - Change CMD to run combined_server
  instead of rest_server - Now serves both REST API (/v1/*) and MCP (/mcp) on port 8045


## v0.4.0 (2026-01-30)

### Chores

- **release**: 0.4.0
  ([`1e356ba`](https://github.com/ardzz/perplexity-scrape/commit/1e356bab7d784727776108e027b6b18209cb383d))

### Features

- Add combined REST API + MCP server entry point
  ([`768a45e`](https://github.com/ardzz/perplexity-scrape/commit/768a45e016148c398b886f7bc41793ab8f8d2bc5))

- Create combined_server.py serving both REST API and MCP on single port (8045) - REST API at
  /v1/... (chat completions, models, health) - MCP HTTP at /mcp (streamable-http transport) -
  Swagger docs at /docs - Add both /mcp and /mcp/ routes to avoid 307 redirect issues - Update
  README with combined server documentation and examples


## v0.3.0 (2026-01-30)

### Chores

- **release**: 0.3.0
  ([`27b0a01`](https://github.com/ardzz/perplexity-scrape/commit/27b0a0104d63163da09e4874a117b7e6add1325c))

### Features

- Add streamable-http transport with auth middleware for MCP server
  ([`5d22337`](https://github.com/ardzz/perplexity-scrape/commit/5d22337de598c7e12258d0f1913cc4e7be135315))


## v0.2.0 (2026-01-30)

### Chores

- **release**: 0.2.0
  ([`031ca1d`](https://github.com/ardzz/perplexity-scrape/commit/031ca1d98e16eb94876de0fba8ad7b69d02742bb))

### Features

- Add optional API key authentication and MCP HTTP transport mode
  ([`bdbbfa4`](https://github.com/ardzz/perplexity-scrape/commit/bdbbfa460af409f98f46a4a1e8569214e0b32f1d))

- Add API key authentication middleware with timing-safe comparison - Support dual MCP transport
  modes (stdio default, HTTP/SSE optional) - Create API key generator script
  (scripts/generate_api_key.py) - Protect /v1/chat/completions and /v1/models endpoints when auth
  enabled - Add pytest infrastructure with 16 passing tests - Update README with authentication and
  MCP HTTP mode documentation - Remove Architecture section from README per user request


## v0.1.1 (2026-01-30)

### Bug Fixes

- **docker**: Remove non-tracked perplexity_research.py from COPY
  ([`9538264`](https://github.com/ardzz/perplexity-scrape/commit/95382643d98fb42d6b07993a0bb9b8d77ab4732e))

File is gitignored and not needed by REST API server

### Chores

- **release**: 0.1.1
  ([`0119e6c`](https://github.com/ardzz/perplexity-scrape/commit/0119e6c78b114d225e50ea0f3c92fe9f0c371d0b))


## v0.1.0 (2026-01-30)

### Bug Fixes

- Align client with reference for history tracking
  ([`1988f79`](https://github.com/ardzz/perplexity-scrape/commit/1988f795c7bc132f8520ffb3320288f54f944ef7))

- Use __Secure-next-auth.session-token cookie for proper auth - Pass cookies as dict instead of
  header string - Add dsl_query, skip_search_enabled, version to payload - Use edge impersonate
  instead of chrome - Add timeout to requests

- **ci**: Correct semantic-release build config
  ([`36bf047`](https://github.com/ardzz/perplexity-scrape/commit/36bf047b1b505d9a98d853fd3b287b1e886c0853))

- Remove invalid build_command=false from pyproject.toml - Add build: false input to GitHub Action
  instead

Fixes validation error in python-semantic-release v9.15.2

### Build System

- Add project dependencies
  ([`eb55b0f`](https://github.com/ardzz/perplexity-scrape/commit/eb55b0f7301ca9ff14c009b242e229502d15a8a7))

- **deps**: Add fastapi and uvicorn for REST API
  ([`645377d`](https://github.com/ardzz/perplexity-scrape/commit/645377dea9e39d7b3b9990ceb14e8f0e43fee598))

New dependencies for OpenAI-compatible REST server:

- fastapi>=0.115.0

- uvicorn[standard]>=0.30.0

- pydantic>=2.0.0

### Chores

- Add development tooling to gitignore
  ([`a64a173`](https://github.com/ardzz/perplexity-scrape/commit/a64a173d3930f23b2604b6affa4d51ee2e5d5f5a))

Exclude local dev tools from version control:

- .opencode/ (opencode SDK)

- .specify/ (speckit templates)

- specs/ (generated specifications)

- .sisyphus/ (work plans)

- Add gitignore for environment files
  ([`89e9f3c`](https://github.com/ardzz/perplexity-scrape/commit/89e9f3c3fc8407cc076fe8fa5a13600c5a779797))

- Ignore perplexity_research.py reference file
  ([`50ac29b`](https://github.com/ardzz/perplexity-scrape/commit/50ac29b16eb8c938bed46cb850b14c7ec98d7236))

- **release**: 0.1.0
  ([`ae12bed`](https://github.com/ardzz/perplexity-scrape/commit/ae12bedaf7bcfc68d3fec404ad2d49de351c22bf))

### Documentation

- Add README with setup and usage instructions
  ([`ec817d2`](https://github.com/ardzz/perplexity-scrape/commit/ec817d2d765ae6becf86cc877e569dd1c64c3d9a))

- Add installation steps and environment configuration - Document MCP config setup for
  Antigravity/Claude Desktop - List available tools and their descriptions

- Update README with REST API and new MCP tools
  ([`31eab94`](https://github.com/ardzz/perplexity-scrape/commit/31eab94a3a0342dc2b8adf8b2b3daa039c650a43))

- Document all 6 MCP tools including research functions

- Add OpenAI-compatible REST API section with endpoints

- Include cURL and Python usage examples

- Add model tables for all 6 providers

- Add environment variables reference

- Add project architecture overview

- Use generic path in MCP config example
  ([`0aab366`](https://github.com/ardzz/perplexity-scrape/commit/0aab366014f5982ddfb5e6c2a74489119698e525))

### Features

- Add MCP server with search tools
  ([`6fc4a23`](https://github.com/ardzz/perplexity-scrape/commit/6fc4a2373e3fb4104d44f111d0eccf998503e155))

- Implement FastMCP server with stdio transport - Add perplexity_ask tool for full search with
  options - Add perplexity_quick_search for simple text responses - Add perplexity_academic_search
  for scholarly sources

- Add model selection to MCP tools and update Kimi to K2.5
  ([`a13abad`](https://github.com/ardzz/perplexity-scrape/commit/a13abaddcf43af669dabdcced222c7ca162787a9))

- Add model_preference parameter to all MCP search tools

- Update Kimi model from K2 to K2.5 (kimik25thinking)

- Add OpenCode provider configuration

- Update README with model selection documentation

- Add Perplexity API client with SSE streaming
  ([`25a3999`](https://github.com/ardzz/perplexity-scrape/commit/25a399938ac8edeb83e1eb0e890fccc81d27c740))

- Implement PerplexityClient class with curl_cffi for Cloudflare bypass - Add SSE stream parsing for
  real-time responses - Extract answer text, citations, and related queries from nested JSON

- Add research and comprehensive search tools
  ([`7455f3b`](https://github.com/ardzz/perplexity-scrape/commit/7455f3b0baa89c382201340099eca52e732930cf))

- Add perplexity_comprehensive_search for web + scholar sources - Add perplexity_research using
  pplx_alpha model for fast research - Remove citations limit in perplexity_ask

- **api**: Add OpenAI-compatible REST API server
  ([`83e4a27`](https://github.com/ardzz/perplexity-scrape/commit/83e4a2733222fd6b24e967bac5af37d2cacd25df))

Implements /v1/chat/completions endpoint compatible with OpenAI API:

Features:

- OpenAI-compatible request/response models

- Streaming (SSE) and non-streaming modes

- Model mapping from OpenAI names to Perplexity

- /v1/models endpoint for listing available models

- Health check endpoint

- Automatic incognito mode (queries won't appear in dashboard)

Run with: python rest_server.py

- **docker**: Add Docker infrastructure and CI/CD pipeline
  ([`655b650`](https://github.com/ardzz/perplexity-scrape/commit/655b65029eeb222047a499a8ae4e08bf0f591d62))

- Add multi-stage Dockerfile with Python 3.12-slim-bookworm - Add docker-compose.yml with health
  check and env_file support - Add GitHub Actions workflow for semantic release and GHCR push - Add
  pyproject.toml with python-semantic-release config - Add .dockerignore and .env.example template

Supports multi-platform builds (amd64/arm64) and conventional commits for automatic semantic
  versioning.

- **server**: Add programming-focused research with category-based prompts
  ([`5011d00`](https://github.com/ardzz/perplexity-scrape/commit/5011d00126145e99ccbd628cc96267cbc15e1082))

- Add PROGRAMMING_RESEARCH_PROMPTS with 6 categories (api, library, implementation, debugging,
  comparison, general) - Modify perplexity_research to use category-based prompt selection - Add
  category normalization (lowercase, strip whitespace) with fallback to 'general' - Add new
  perplexity_general_research function preserving original generic/academic prompt

Each programming prompt template requests: - Complete, runnable code examples with imports - Version
  compatibility information - Error handling patterns - Best practices and common pitfalls

### Refactoring

- **client**: Improve code style and add incognito mode
  ([`025db2f`](https://github.com/ardzz/perplexity-scrape/commit/025db2f13d5bd8b71f6ad56d09299452a68642e7))

Style improvements:

- Consistent whitespace formatting

- Vertical list formatting for readability

Features:

- Add is_incognito parameter to hide queries from dashboard

- Increase timeout to 1800s for long-running queries

- **server**: Replace math-specific prompt with general research prompt
  ([`c159d00`](https://github.com/ardzz/perplexity-scrape/commit/c159d00a5e9420aef1bd3bb3973aec767bfcfde2))

### Testing

- Add client test script
  ([`993eec8`](https://github.com/ardzz/perplexity-scrape/commit/993eec86dff9aac1276e662395a8d9660b387c0b))

- Add test_basic_query function for streaming validation - Verify SSE event parsing and response
  structure
