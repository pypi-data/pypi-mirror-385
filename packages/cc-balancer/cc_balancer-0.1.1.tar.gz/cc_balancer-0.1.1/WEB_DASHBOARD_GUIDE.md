# CC-Balancer Web Dashboard Guide

## Overview

CC-Balancer now includes a modern enterprise-grade SaaS Web Dashboard for monitoring and managing your Claude Code proxy. The dashboard provides real-time metrics, provider status monitoring, routing configuration, and performance analytics.

## Features

### Dashboard Capabilities
- **Real-time Metrics**: Live monitoring of request count, success rate, average latency, and active providers
- **Performance Analytics**: P50/P95/P99 latency percentiles for detailed performance insights
- **Provider Management**: View status, configuration, and health of all configured providers
- **Routing Configuration**: Display current routing strategy and failover settings
- **Auto-refresh**: Dashboard updates every 5 seconds automatically

### Design Highlights
- Modern enterprise SaaS UI with Inter font and HSL theme variables
- Responsive card-based layout with smooth hover effects
- Neutral gray + brand blue color scheme
- Professional and clean design aesthetic

## Architecture

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom HSL theme
- **Backend**: FastAPI with RESTful API
- **Real-time**: WebSocket support for live metrics streaming

### Integration
- Frontend static files are embedded in the FastAPI application
- Single-service deployment: one command starts both backend and dashboard
- Development proxy: Frontend dev server proxies API requests to backend

## Quick Start

### Installation
```bash
# Install CC-Balancer (includes Web Dashboard)
pip install -e .
```

### Start Server
```bash
# Start CC-Balancer with default config
cc-balancer

# Or with custom config
cc-balancer --config config.yaml

# Custom host/port
cc-balancer --host 0.0.0.0 --port 8080
```

### Access Dashboard
Once the server starts, access the Web Dashboard at:
```
http://localhost:8000
```

The dashboard will automatically connect to the backend API and display:
- Real-time request metrics
- Provider status and configuration
- Routing strategy settings
- Performance statistics

## API Endpoints

The dashboard consumes the following REST API endpoints:

### Dashboard Metrics
- `GET /api/v1/dashboard/summary` - High-level metrics summary
- `GET /api/v1/dashboard/metrics` - Detailed metrics with time series

### Provider Management
- `GET /api/v1/providers/` - List all providers
- `POST /api/v1/providers/` - Create new provider
- `DELETE /api/v1/providers/{name}` - Remove provider
- `POST /api/v1/providers/{name}/test` - Test provider connection

### Routing Configuration
- `GET /api/v1/routing/config` - Get routing settings
- `PUT /api/v1/routing/config` - Update routing settings

### Monitoring
- `GET /api/v1/monitoring/latency` - Latency percentiles (P50/P95/P99)
- `GET /api/v1/monitoring/requests` - Request history

### Real-time Updates
- `WebSocket /api/v1/ws/realtime` - Live metrics streaming

## Development

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Build for production
npm run build
```

The development server runs on `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

### Backend Development
```bash
# Start backend with auto-reload
cc-balancer --reload

# Run with custom config for testing
cc-balancer --config config.test.yaml --reload
```

## Metrics Collection

The dashboard displays metrics collected by the `MetricsCollector` class:

### Tracked Metrics
- **Request Count**: Total number of proxied requests
- **Success Rate**: Percentage of successful requests (HTTP 2xx)
- **Average Latency**: Mean response time in milliseconds
- **Latency Percentiles**: P50/P95/P99 for performance analysis
- **Provider Distribution**: Requests per provider
- **Time Series**: Requests per minute for trend analysis

### Thread Safety
The metrics collector uses thread-safe operations with `threading.Lock` and `collections.deque` for concurrent request tracking.

## Deployment

### Production Build
```bash
# Build frontend for production
cd frontend
npm run build

# Frontend assets are output to: ../cc_balancer/static/
```

### Single Command Deployment
```bash
# Install and run
pip install -e .
cc-balancer

# Dashboard automatically available at http://localhost:8000
```

### Docker Deployment (Future)
```dockerfile
# Dockerfile example for future containerization
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
EXPOSE 8000
CMD ["cc-balancer"]
```

## Configuration

### Server Settings
Configure via `config.yaml`:
```yaml
server:
  host: "127.0.0.1"
  port: 8000
  log_level: "INFO"
  reload: false
```

### Dashboard Customization
Frontend theme variables in `frontend/src/index.css`:
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  /* ... more theme variables */
}
```

## Troubleshooting

### Dashboard Not Loading
1. Verify static files exist: `ls cc_balancer/static/`
2. Check server logs for "Web Dashboard static files mounted"
3. Ensure no other service is using port 8000

### API Connection Issues
1. Verify backend is running: `curl http://localhost:8000/healthz`
2. Check CORS settings if accessing from different origin
3. Review browser console for API errors

### Build Issues
```bash
# Clear and rebuild
cd frontend
rm -rf dist node_modules
npm install
npm run build
```

## Browser Compatibility

The Web Dashboard supports modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

Requires JavaScript enabled and WebSocket support for real-time updates.

## Future Enhancements

Planned features for future releases:
- [ ] Authentication and authorization
- [ ] Provider configuration via UI
- [ ] Historical metrics and charting
- [ ] Alert configuration and notifications
- [ ] Request inspection and debugging tools
- [ ] Multi-language support
- [ ] Dark mode toggle

## License

See [LICENSE](LICENSE) file in project root.

## Support

For issues and feature requests, please open an issue on GitHub or refer to the main [README.md](README.md) for project documentation.
