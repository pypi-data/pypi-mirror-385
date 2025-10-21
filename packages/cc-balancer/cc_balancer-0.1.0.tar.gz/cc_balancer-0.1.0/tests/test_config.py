"""
Tests for configuration loading and validation.
"""

import os
import tempfile
from pathlib import Path

import pytest

from cc_balancer.config import AppConfig, ProviderConfig
from cc_balancer.config_loader import ConfigError, expand_env_vars, load_config


def test_expand_env_vars():
    """Test environment variable expansion."""
    os.environ["TEST_VAR"] = "test_value"

    assert expand_env_vars("${TEST_VAR}") == "test_value"
    assert expand_env_vars("prefix_${TEST_VAR}_suffix") == "prefix_test_value_suffix"
    assert expand_env_vars("${NONEXISTENT}") == "${NONEXISTENT}"

    del os.environ["TEST_VAR"]


def test_load_valid_config():
    """Test loading valid configuration."""
    config_content = """
server:
  host: "127.0.0.1"
  port: 8080
  log_level: "DEBUG"

routing:
  strategy: "round-robin"

cache:
  enabled: true
  ttl_seconds: 30

error_handling:
  failure_threshold: 5
  recovery_interval_seconds: 60

providers:
  - name: "test-provider"
    base_url: "https://api.example.com"
    auth_type: "api_key"
    api_key: "test-key"
    weight: 1
    priority: 1
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        f.flush()

        try:
            config = load_config(f.name)

            assert config.server.host == "127.0.0.1"
            assert config.server.port == 8080
            assert config.server.log_level == "DEBUG"
            assert config.routing.strategy == "round-robin"
            assert len(config.providers) == 1
            assert config.providers[0].name == "test-provider"
        finally:
            os.unlink(f.name)


def test_config_validation_duplicate_names():
    """Test that duplicate provider names are rejected."""
    with pytest.raises(ValueError, match="Duplicate provider names"):
        AppConfig(
            providers=[
                ProviderConfig(
                    name="duplicate",
                    base_url="https://api1.example.com",
                    auth_type="api_key",
                    api_key="key1",
                ),
                ProviderConfig(
                    name="duplicate",
                    base_url="https://api2.example.com",
                    auth_type="api_key",
                    api_key="key2",
                ),
            ]
        )


def test_config_validation_api_key_required():
    """Test that api_key is required for api_key auth type."""
    with pytest.raises(ValueError, match="api_key required"):
        ProviderConfig(
            name="test",
            base_url="https://api.example.com",
            auth_type="api_key",
            api_key=None,
        )


def test_load_nonexistent_config():
    """Test that loading nonexistent config raises error."""
    with pytest.raises(ConfigError, match="not found"):
        load_config("/nonexistent/config.yaml")
