# CC-Balancer - Quick Reference

## 🚀 Quick Start

### 1. Start CC-Balancer
```bash
cc-balancer
```

### 2. Configure Claude Code
Copy the Base URL shown on screen and paste into Claude Code settings:
```
http://localhost:8080
```

### 3. Verify
```bash
curl http://localhost:8080/healthz
```

## 📋 Command Options

```bash
# Basic
cc-balancer

# Custom port
cc-balancer --port 3000

# Custom host (network access)
cc-balancer --host 0.0.0.0

# Custom config file
cc-balancer --config custom.yaml

# Development mode (auto-reload)
cc-balancer --reload

# Combine options
cc-balancer --host 0.0.0.0 --port 3000 --reload
```

## 🔧 Claude Code Setup

### Method 1: Settings UI (Recommended)
1. Open Claude Code Settings (⚙️)
2. Find "Anthropic API Settings"
3. Set Base URL: `http://localhost:8080`
4. Keep your existing API key

### Method 2: Environment Variables
```bash
# Add to ~/.bashrc or ~/.zshrc
export ANTHROPIC_BASE_URL="http://localhost:8080"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Reload shell
source ~/.bashrc
```

## 📊 Display Overview

### What You'll See on Startup

```
┌─────────────────────────────────────────┐
│ ASCII Banner                            │
│ "CC-Balancer"                          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🚀 Server Configuration                 │
│ - Host, Port, Log Level, Auto-Reload   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔀 Routing & Resilience                 │
│ - Strategy, Thresholds, Cache          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔌 Provider Configuration               │
│ - Table of all providers                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔧 Claude Code Configuration            │
│ - Base URL and endpoints                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 📝 Quick Setup Guide                    │
│ - 3-step configuration                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🌍 Environment Variables                │
│ - Alternative setup method              │
└─────────────────────────────────────────┘
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8080/healthz
```

### Test Request
```bash
curl -X POST http://localhost:8080/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Run Demo
```bash
python examples/cli_demo.py
```

## 📝 Configuration File

### Minimal Example
```yaml
# config.yaml
server:
  host: "127.0.0.1"
  port: 8080

providers:
  - name: anthropic
    base_url: https://api.anthropic.com
    api_key: ${ANTHROPIC_API_KEY}
```

### Full Example
```yaml
server:
  host: "0.0.0.0"
  port: 8080
  log_level: INFO
  reload: false

routing:
  strategy: weighted

cache:
  enabled: true
  ttl_seconds: 60
  max_size: 1000

error_handling:
  failure_threshold: 3
  recovery_interval_seconds: 30
  retry_backoff: [1, 2, 4, 8, 30]

providers:
  - name: primary
    base_url: https://api.anthropic.com
    api_key: ${PRIMARY_KEY}
    weight: 2
    priority: 1
    timeout_seconds: 30

  - name: backup
    base_url: https://api.anthropic.com
    api_key: ${BACKUP_KEY}
    weight: 1
    priority: 2
    timeout_seconds: 30
```

## 🔍 Troubleshooting

### Connection Refused
```bash
# Check if CC-Balancer is running
curl http://localhost:8080/healthz

# Check port
lsof -i :8080

# Try different address
curl http://127.0.0.1:8080/healthz
```

### Wrong URL
✅ Correct: `http://localhost:8080`
❌ Wrong: `https://localhost:8080`
❌ Wrong: `http://localhost:8080/`
❌ Wrong: `localhost:8080`

### Logs
```bash
# Start with verbose logging
cc-balancer --config config.yaml
# Logs appear in terminal
```

## 📚 Documentation

- `README.md` - Project overview
- `docs/CLI_DISPLAY.md` - CLI features
- `docs/CLAUDE_CODE_SETUP.md` - Setup guide
- `docs/BANNER_COMPARISON.md` - Banner design
- `FINAL_CLI_SUMMARY.md` - Complete summary

## 🎯 Key Features

✅ ASCII Art Banner
✅ Structured Configuration Display
✅ Provider Table
✅ Automatic Claude Code Config
✅ Multiple Setup Methods
✅ Smart URL Detection
✅ Color-Coded Panels
✅ Copy-Paste Ready

## 💡 Tips

1. **First Time**: Just run `cc-balancer` and follow the on-screen instructions
2. **Network Access**: Use `--host 0.0.0.0` for team setups
3. **Development**: Add `--reload` for automatic code reloading
4. **Multiple Providers**: Configure multiple API keys for load balancing
5. **Verification**: Always check `/healthz` after configuration changes

## 🔗 Quick Links

- Health Check: `http://localhost:8080/healthz`
- API Docs: `http://localhost:8080/docs`
- Root Info: `http://localhost:8080/`

## ⚡ Common Commands

```bash
# Start
cc-balancer

# Stop
Ctrl+C

# Restart
cc-balancer

# Check config
cc-balancer --config config.yaml

# Test
curl http://localhost:8080/healthz
```

---

**Need Help?** Check `docs/CLAUDE_CODE_SETUP.md` for detailed instructions.
