"""
Test API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from cc_balancer.main import app

client = TestClient(app)


def test_dashboard_summary():
    """Test dashboard summary endpoint."""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "success_rate" in data
    assert "avg_latency_ms" in data
    assert "requests_per_minute" in data
    assert isinstance(data["requests_per_minute"], list)


def test_dashboard_metrics():
    """Test dashboard metrics endpoint."""
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "requests_timeline" in data
    assert "provider_distribution" in data
    assert "latency_buckets" in data
    assert isinstance(data["requests_timeline"], list)
    assert isinstance(data["provider_distribution"], list)


def test_list_providers():
    """Test list providers endpoint."""
    response = client.get("/api/v1/providers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have providers from config
    assert len(data) >= 1


def test_routing_config():
    """Test routing config endpoint."""
    response = client.get("/api/v1/routing/config")
    assert response.status_code == 200
    data = response.json()
    assert "strategy" in data
    assert "failure_threshold" in data
    assert "recovery_interval_seconds" in data
    assert "cache_enabled" in data
    assert "cache_ttl_seconds" in data


def test_monitoring_latency():
    """Test latency stats endpoint."""
    response = client.get("/api/v1/monitoring/latency")
    assert response.status_code == 200
    data = response.json()
    assert "p50" in data
    assert "p95" in data
    assert "p99" in data


def test_monitoring_requests():
    """Test request history endpoint."""
    response = client.get("/api/v1/monitoring/requests?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert "requests" in data
    assert "total" in data
    assert isinstance(data["requests"], list)


def test_healthz():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "providers" in data


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CC-Balancer"
    assert data["status"] == "running"
