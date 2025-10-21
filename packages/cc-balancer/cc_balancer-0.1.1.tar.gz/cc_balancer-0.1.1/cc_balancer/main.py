"""
Main FastAPI application for CC-Balancer.
"""

import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

import httpx
import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from cc_balancer.api.v1 import (
    dashboard_router,
    monitoring_router,
    providers_router,
    routing_router,
)
from cc_balancer.api.websocket import websocket_realtime_metrics
from cc_balancer.config_loader import ConfigError, load_config_with_defaults
from cc_balancer.core.metrics import metrics_collector
from cc_balancer.core.state import app_state
from cc_balancer.providers import ProviderRegistry, create_provider
from cc_balancer.router import (
    RoundRobinStrategy,
    RouterEngine,
    RoutingStrategy,
    WeightedStrategy,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager for startup and shutdown.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting CC-Balancer")

    try:
        # Load configuration from environment variable (survives reload)
        config_path = Path(os.environ.get("CC_BALANCER_CONFIG_PATH", "config.yaml"))
        config = load_config_with_defaults(config_path)
        app_state.config = config
        logger.info(
            "Configuration loaded",
            providers=len(config.providers),
            routing_strategy=config.routing.strategy,
        )

        # Initialize provider registry
        registry = ProviderRegistry()
        for provider_config in config.providers:
            provider = create_provider(provider_config)
            registry.register(provider)
            logger.info(
                "Provider registered",
                name=provider.name,
                auth_type=provider_config.auth_type,
            )
        app_state.provider_registry = registry

        # Initialize routing engine
        strategy: RoutingStrategy
        if config.routing.strategy == "round-robin":
            strategy = RoundRobinStrategy()
        else:
            strategy = WeightedStrategy()

        app_state.router = RouterEngine(strategy)
        logger.info("Router initialized", strategy=config.routing.strategy)

        logger.info("CC-Balancer started successfully")

    except ConfigError as e:
        logger.error("Configuration error", error=str(e))
        sys.exit(1)
    except Exception as e:
        logger.error("Startup failed", error=str(e))
        sys.exit(1)

    yield

    # Shutdown
    logger.info("Shutting down CC-Balancer")
    if app_state.provider_registry:
        await app_state.provider_registry.close_all()
    logger.info("CC-Balancer shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="CC-Balancer",
    description="Intelligent proxy for Claude Code with automatic failover and load balancing",
    version="0.1.0",
    lifespan=lifespan,
)


# Metrics collection middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # Only track proxy requests
        if not request.url.path.startswith("/v1/messages"):
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Get selected provider from request state
        provider_name = getattr(request.state, "selected_provider", "unknown")

        # Record metrics
        metrics_collector.record_request(
            provider=provider_name,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
        )

        return response


# Add middleware
app.add_middleware(MetricsMiddleware)

# Register API routers
app.include_router(dashboard_router)
app.include_router(providers_router)
app.include_router(routing_router)
app.include_router(monitoring_router)


# WebSocket endpoint
@app.websocket("/api/v1/ws/realtime")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time metrics."""
    await websocket_realtime_metrics(websocket)


# Static files for Web Dashboard
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    logger.info("Web Dashboard static files mounted", path=str(static_dir))


@app.get("/healthz")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns:
        JSON response with health status
    """
    if not app_state.provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")

    providers = app_state.provider_registry.get_all()
    if not providers:
        raise HTTPException(status_code=503, detail="No providers configured")

    # For Phase 1, just check if providers are registered
    # Phase 3 will add actual health monitoring
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "providers": len(providers),
            "provider_names": [p.name for p in providers],
        },
    )


@app.post("/v1/messages")
async def proxy_messages(request: Request) -> Response:
    """
    Proxy endpoint for Claude API messages.

    Args:
        request: FastAPI request object

    Returns:
        Proxied response from provider
    """
    if not app_state.router or not app_state.provider_registry:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Get available providers
    providers = app_state.provider_registry.get_healthy()
    if not providers:
        raise HTTPException(status_code=503, detail="No healthy providers available")

    # Select provider using routing strategy
    provider = app_state.router.select_provider(providers)

    # Store provider name in request state for metrics collection
    request.state.selected_provider = provider.name

    logger.info("Routing request", provider=provider.name)

    try:
        # Get request body
        body = await request.json()

        # Construct full path with query parameters if present
        # Filter out unsupported parameters (some providers don't support beta)
        path = "/v1/messages"
        if request.url.query:
            # Parse and filter query parameters
            from urllib.parse import parse_qs, urlencode

            params = parse_qs(str(request.url.query))
            # Remove 'beta' parameter as many providers don't support it
            params.pop("beta", None)
            if params:
                # Rebuild query string from remaining params
                query_string = urlencode(params, doseq=True)
                path = f"{path}?{query_string}"

        # Filter headers - remove hop-by-hop headers that shouldn't be forwarded
        # HTTPX will set correct Content-Length when sending json_data
        # Also filter out authentication headers - provider will add its own
        filtered_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower()
            not in {
                "host",
                "content-length",
                "content-type",
                "connection",
                "transfer-encoding",
                "te",
                "trailer",
                "upgrade",
                "authorization",
                "x-api-key",
            }
        }

        # Log request details for debugging
        logger.debug(
            "1Forwarding request to provider",
            provider=provider.name,
            path=path,
            headers=dict(filtered_headers),
            body_keys=list(body.keys()) if isinstance(body, dict) else "non-dict",
        )

        # Forward request to provider
        response = await provider.send_request(
            method="POST",
            path=path,
            headers=filtered_headers,
            json_data=body,
        )

        # HTTPX automatically decodes the response based on content-encoding
        # So we use response.content (decoded) and remove content-encoding header
        # to avoid double-decompression by the client

        # Filter response headers before returning
        # Convert to dict and explicitly filter hop-by-hop headers
        response_headers = dict(response.headers)

        # Remove hop-by-hop headers that should not be forwarded
        # Also remove content-encoding since we're returning decoded content
        headers_to_remove = [
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
            "proxy-connection",
            "content-encoding",
        ]
        for header in headers_to_remove:
            response_headers.pop(header, None)

        # Create a custom Response that bypasses default header handling
        # We need to use init_headers parameter which is passed to __init__
        class ProxyResponse(Response):
            def __init__(self, content, status_code, custom_headers):
                # Convert to raw_headers format
                self.raw_headers = [
                    (k.encode("latin-1"), v.encode("latin-1")) for k, v in custom_headers.items()
                ]
                super().__init__(content=content, status_code=status_code)
                # Override the init_headers method to prevent default headers
                self.init_headers(custom_headers)

        # Log response details for debugging
        if response.status_code >= 400:
            logger.warning(
                "Provider returned error response",
                provider=provider.name,
                status_code=response.status_code,
                response_body=response.content[:500].decode("utf-8", errors="replace"),
                request_path=path,
            )

        # Return provider response with filtered headers
        # response.content is already decoded by HTTPX
        return ProxyResponse(
            content=response.content,
            status_code=response.status_code,
            custom_headers=response_headers,
        )

    except httpx.HTTPError as e:
        logger.error(
            "HTTP error from provider",
            provider=provider.name,
            error_type=type(e).__name__,
            error=str(e),
        )
        raise HTTPException(status_code=502, detail=f"Provider HTTP error: {type(e).__name__}")
    except Exception as e:
        logger.error(
            "Request processing failed",
            provider=provider.name,
            error_type=type(e).__name__,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Internal error: {type(e).__name__}")


@app.get("/")
async def root() -> FileResponse:
    """
    Serve Web Dashboard index page.

    Returns:
        Web Dashboard HTML
    """
    static_index = static_dir / "index.html"
    if static_index.exists():
        return FileResponse(static_index)
    # Fallback to API info if dashboard not built
    return JSONResponse({
        "service": "CC-Balancer",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/healthz",
    })


@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> FileResponse:
    """
    SPA fallback route for Web Dashboard.

    Serves index.html for all non-API routes to enable client-side routing.

    Args:
        full_path: Request path

    Returns:
        Web Dashboard HTML or 404
    """
    # Skip API routes, docs, and health check
    if full_path.startswith(("api/", "v1/", "healthz", "docs", "redoc", "openapi.json", "assets/")):
        raise HTTPException(status_code=404, detail="Not found")

    # Serve dashboard index for all other routes
    static_index = static_dir / "index.html"
    if static_index.exists():
        return FileResponse(static_index)
    raise HTTPException(status_code=404, detail="Web Dashboard not found")


def cli() -> None:
    """Command-line interface entry point."""
    import argparse

    from cc_balancer.cli_display import (
        print_banner,
        print_claude_code_config,
        print_config_info,
        print_error,
        print_startup_success,
    )

    parser = argparse.ArgumentParser(description="CC-Balancer - Intelligent proxy for Claude Code")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--host",
        type=str,
        help="Server host (overrides config)",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Server port (overrides config)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development only)",
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Store config path in environment variable for lifespan to use (survives reload)
    if args.config:
        os.environ["CC_BALANCER_CONFIG_PATH"] = str(Path(args.config).absolute())

    # Load config to get server settings
    config_path = Path(os.environ.get("CC_BALANCER_CONFIG_PATH", "config.yaml"))
    try:
        config = load_config_with_defaults(config_path)
    except ConfigError as e:
        print_error("Configuration Error", str(e))
        sys.exit(1)

    # Override with CLI arguments
    host = args.host or config.server.host
    port = args.port or config.server.port
    reload = args.reload or config.server.reload

    # Print configuration info
    print_config_info(config, host, port, reload)

    # Print startup success message
    print_startup_success(len(config.providers), host, port)

    # Print Claude Code configuration guide
    print_claude_code_config(host, port)

    # Run server
    uvicorn.run(
        "cc_balancer.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=config.server.log_level.lower(),
    )


if __name__ == "__main__":
    cli()
