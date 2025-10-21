# Changelog

All notable changes to CC-Balancer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.1] - 2025-10-21

### Fixed
- 🔧 **Static files inclusion in PyPI package**
  - Added MANIFEST.in to include Web Dashboard static assets
  - Updated pyproject.toml with package-data configuration
  - Web Dashboard now accessible at http://localhost:8000/ after pip install

### Added
- 📦 MANIFEST.in for explicit file inclusion
- 🔧 setuptools.package-data configuration for static files

## [0.1.0] - 2025-10-21

### Added - Phase 1 Foundation
- ✅ FastAPI async application with lifespan management
- ✅ Pydantic v2 configuration models with comprehensive validation
- ✅ YAML configuration loader with `${VAR}` environment variable expansion
- ✅ Provider abstraction layer (APIKeyProvider, OAuthProvider skeleton)
- ✅ ProviderRegistry for dynamic provider management
- ✅ Routing engine with pluggable strategies
  - RoundRobinStrategy for equal distribution
  - WeightedStrategy for priority-based distribution
- ✅ FastAPI endpoints:
  - `POST /v1/messages` - Proxy requests to providers
  - `GET /healthz` - Health check
  - `GET /` - Service information
  - `GET /docs` - Auto-generated OpenAPI documentation
- ✅ CLI interface with argparse
- ✅ Structured JSON logging with structlog
- ✅ Comprehensive documentation (README, DEVELOPMENT, STATUS, TESTING)
- ✅ Test suite with integration and unit tests

### Fixed
- 🔧 **Content-Length header issue** in proxy endpoint
  - Problem: Original Content-Length from client forwarded to provider
  - Solution: Filter hop-by-hop headers (host, content-length, content-type, etc.)
  - Result: HTTPX now correctly handles Content-Length calculation
  - Commit: `f39a680`

- 🔧 **Config path not passed from CLI to lifespan**
  - Problem: `--config` parameter ignored, always loaded config.yaml
  - Solution: Store config path in AppState, use in lifespan
  - Result: Specified config files now correctly loaded
  - Commit: `9c6edc8`

### Technical Details

#### Configuration System
- ServerConfig: host, port, log_level, reload
- RoutingConfig: strategy (round-robin, weighted)
- CacheConfig: enabled, ttl_seconds, max_size
- ErrorHandlingConfig: failure_threshold, recovery_interval, retry_backoff
- ProviderConfig: name, base_url, auth_type, api_key, weight, priority

#### Provider Management
- Abstract Provider base class with unified interface
- APIKeyProvider with Bearer token authentication
- ProviderRegistry for dynamic provider management
- HTTPX async client integration

#### Routing Engine
- RouterEngine with strategy pattern
- Protocol-based Provider interface for type safety
- Round-robin: Equal distribution across providers
- Weighted: Priority-based distribution by weight

### Testing
- `test_startup.py` - Integration test for startup sequence
- `test_fix.py` - Verification test for header filtering
- `test_config_loading.py` - Configuration loading validation
- `tests/test_config.py` - Configuration model tests
- `tests/test_router.py` - Routing strategy tests

### Documentation
- **README.md** - User guide and quick start
- **DEVELOPMENT.md** - Developer guide with Phase 3 roadmap
- **STATUS.md** - Current status tracking
- **TESTING.md** - Comprehensive testing guide
- **CHANGELOG.md** - This file

### Known Limitations (By Design)
- No health monitoring yet (Phase 3)
- No circuit breaker yet (Phase 3)
- No request caching yet (Phase 4)
- No Prometheus metrics yet (Phase 5)
- OAuth support skeleton only (Phase 6)
- No admin endpoints yet (Phase 8)

## [Unreleased]

### Planned - Phase 3: Health Monitoring & Failover
- [ ] HealthMonitor class with circuit breaker pattern
- [ ] Background health check tasks
- [ ] Exponential backoff retry (1s → 2s → 4s → 8s → 30s)
- [ ] Automatic provider failover
- [ ] Provider health states (healthy, degraded, unhealthy)

### Planned - Phase 4: Advanced Features
- [ ] Request deduplication cache
- [ ] TTL-based LRU cache
- [ ] Cross-provider caching

### Planned - Phase 5: Observability
- [ ] Prometheus metrics endpoint
- [ ] Request correlation IDs
- [ ] Performance tracking

### Planned - Phase 6: OAuth Support
- [ ] Full OAuth 2.0 flow implementation
- [ ] Token management and refresh

### Planned - Phase 8: Admin Endpoints
- [ ] Dynamic configuration updates
- [ ] Provider management API

## Version History

- **v0.1.0** (2025-10-16) - Phase 1 Foundation + Bug Fixes
- **Upcoming** - Phase 3: Health Monitoring & Failover

## Commits

### Phase 1 Implementation
- `cd397f5` - feat: Phase 1 Foundation - CC-Balancer MVP implementation
- `d8f2a68` - docs: Add comprehensive STATUS.md tracking document

### Bug Fixes
- `f39a680` - fix: Resolve Content-Length header issue in proxy endpoint
- `0563c95` - test: Add verification test for proxy header filtering fix
- `9c6edc8` - fix: Config path not passed from CLI to lifespan

## Migration Guide

### From Development to Production

1. **Update Configuration**
   ```yaml
   server:
     log_level: "WARNING"  # Reduce verbosity
     reload: false         # Disable auto-reload
   ```

2. **Set Environment Variables**
   ```bash
   export ANTHROPIC_API_KEY="your-production-key"
   export ANTHROPIC_BACKUP_KEY="your-backup-key"
   ```

3. **Run with Production Config**
   ```bash
   cc-balancer --config config.production.yaml
   ```

### Breaking Changes
None yet (v0.1.0 is initial release)

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines and Phase 3 implementation plan.

## License

MIT License - See LICENSE file for details
