# CC-Balancer

Intelligent proxy for Claude Code with automatic failover, load balancing, and cost optimization across multiple API providers.

## Features

**Phase 1 (Current - MVP Foundation)**
- ✅ FastAPI-based async proxy server
- ✅ Pydantic v2 configuration with YAML support
- ✅ Environment variable expansion (`${VAR_NAME}`)
- ✅ Multiple routing strategies (round-robin, weighted)
- ✅ API key authentication
- ✅ Basic health check endpoint
- ✅ Provider abstraction layer

**Coming Soon**
- 🔄 Health monitoring with automatic failover (Phase 3)
- 📊 Prometheus metrics and structured logging (Phase 5)
- 🔒 OAuth 2.0 support (Phase 6)
- 💾 Request deduplication cache (Phase 4)
- 🎛️ Admin API for dynamic configuration (Phase 8)

## Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd CC-B
```

2. **Install dependencies**
```bash
# Using pip
pip install -e .

# Or using uv (recommended)
uv pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

3. **Configure providers**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

4. **Review configuration**
```bash
# Edit config.yaml to adjust provider settings
nano config.yaml
```

### Running the Server

```bash
# Start the server
cc-balancer

# Or with custom config
cc-balancer --config /path/to/config.yaml

# Development mode with auto-reload
cc-balancer --reload

# Custom host and port
cc-balancer --host 127.0.0.1 --port 8080
```

The server will start on `http://0.0.0.0:8000` by default.

### config Claude Code
```
# 配置环境变量
export ANTHROPIC_BASE_URL=http://localhost:8000
```

### Testing the Setup

```bash
# Check health
curl http://localhost:8000/healthz

# Test proxy (requires valid API key in config)
curl "http://localhost:8000/v1/messages" \
     -H "x-api-key: sk-xxxx" \
     -H "anthropic-version: 2023-06-01" \
     -H "Content-Type: application/json" \
     -d '{
           "model": "claude-sonnet-4-20250514",
           "max_tokens": 1024,
           "messages": [
             {"role": "user", "content": "Hello, Claude"}
           ]
         }'

respose example:
{"model":"claude-sonnet-4-20250514","id":"msg_0198XFCY8VW5cq131jNsJptD","type":"message","role":"assistant","content":[{"type":"text","text":"Hello! It's nice to meet you. How are you doing today? Is there anything I can help you with or would you like to chat about something in particular?"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":10,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":37,"service_tier":"standard"}} 
```

### API Documentation

FastAPI provides automatic interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Configuration is managed through `config.yaml` with environment variable support.

### Example Configuration

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  log_level: "INFO"

routing:
  strategy: "weighted"  # or "round-robin"

providers:
  - name: "anthropic-primary"
    base_url: "https://api.anthropic.com"
    auth_type: "api_key"
    api_key: "${ANTHROPIC_API_KEY}"
    weight: 2  # Receives 2x traffic
    priority: 1
```

### Environment Variables

Set in `.env` file or export directly:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export ANTHROPIC_BACKUP_KEY="sk-ant-backup-key-here"
```

## Architecture

### Components

- **Router Engine**: Intelligent request routing with configurable strategies
- **Provider Abstraction**: Unified interface for different authentication types
- **Config Loader**: YAML-based configuration with validation
- **Health Monitor**: (Coming in Phase 3) Provider health tracking

### Routing Strategies

**Round-Robin**: Equal distribution across all providers
```yaml
routing:
  strategy: "round-robin"
```

**Weighted**: Distribution based on provider weights
```yaml
routing:
  strategy: "weighted"

providers:
  - name: "primary"
    weight: 3  # Gets 75% of traffic
  - name: "backup"
    weight: 1  # Gets 25% of traffic
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=cc_balancer --cov-report=html

# Type checking
mypy cc_balancer

# Code formatting
black cc_balancer tests
ruff check cc_balancer tests
```

### Project Structure

```
CC-B/
├── cc_balancer/          # Main package
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── config.py        # Pydantic models
│   ├── config_loader.py # YAML config loading
│   ├── router.py        # Routing strategies
│   └── providers.py     # Provider abstraction
├── tests/               # Test suite
├── config.yaml          # Configuration
├── pyproject.toml       # Package metadata
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_router.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=cc_balancer --cov-report=term-missing
```

## Roadmap

### Phase 1: Foundation ✅ (Current)
- FastAPI skeleton + Pydantic models
- YAML config loading
- Basic health endpoint
- Round-robin routing

### Phase 2: Provider Abstraction ✅ (Current)
- Provider abstract base class
- APIKeyProvider implementation
- ProviderRegistry

### Phase 3: Health & Failover (Next)
- HealthMonitor with failure tracking
- Circuit breaker logic
- Background health checks
- Automatic failover

### Phase 4: Advanced Features
- Request deduplication cache
- Weighted routing optimization
- OAuth provider (deferred to Phase 6)

### Phase 5: Observability
- Prometheus metrics
- Structured JSON logging
- Performance tracking

### Phase 6: OAuth Support
- OAuth 2.0 flow implementation
- Token management

## Performance

**Target Metrics** (to be validated in Phase 9):
- Proxy latency overhead: <50ms (p95)
- Concurrent requests: 100+ without degradation
- Memory usage: <512MB under normal load

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and type checking
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- Documentation: [GitHub README](https://github.com/yourusername/cc-balancer)
- Issues: [GitHub Issues](https://github.com/yourusername/cc-balancer/issues)
