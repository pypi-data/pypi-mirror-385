"""
Tests for CLI display utilities.
"""

from io import StringIO
from unittest.mock import patch

from cc_balancer.cli_display import (
    _format_bool,
    _truncate_url,
    print_banner,
    print_error,
    print_shutdown,
    print_startup_success,
)
from cc_balancer.config import AppConfig, ProviderConfig, ServerConfig


def test_format_bool() -> None:
    """Test boolean formatting."""
    assert "[green]" in _format_bool(True)
    assert "[dim]" in _format_bool(False)


def test_truncate_url() -> None:
    """Test URL truncation."""
    short_url = "https://example.com"
    assert _truncate_url(short_url) == short_url

    long_url = "https://example.com/very/long/path/that/exceeds/limit"
    truncated = _truncate_url(long_url, max_length=20)
    assert len(truncated) <= 20
    assert "..." in truncated


def test_print_banner() -> None:
    """Test banner printing."""
    with patch("sys.stdout", new=StringIO()) as fake_out:
        print_banner()
        output = fake_out.getvalue()
        assert "CC-Balancer" in output or "Balancer" in output


def test_print_startup_success() -> None:
    """Test startup success message."""
    with patch("sys.stdout", new=StringIO()) as fake_out:
        print_startup_success(3)
        output = fake_out.getvalue()
        assert "3" in output
        assert "provider" in output.lower()


def test_print_error() -> None:
    """Test error message printing."""
    with patch("sys.stdout", new=StringIO()) as fake_out:
        print_error("Test Error", "This is a test error message")
        output = fake_out.getvalue()
        assert "Test Error" in output
        assert "test error message" in output.lower()


def test_print_shutdown() -> None:
    """Test shutdown message."""
    with patch("sys.stdout", new=StringIO()) as fake_out:
        print_shutdown()
        output = fake_out.getvalue()
        assert "shutdown" in output.lower()


def test_print_config_info_basic() -> None:
    """Test basic config info printing."""
    # Create minimal config
    config = AppConfig(
        server=ServerConfig(),
        providers=[
            ProviderConfig(
                name="test-provider",
                base_url="https://api.example.com",
                api_key="test-key",
            )
        ],
    )

    with patch("sys.stdout", new=StringIO()) as fake_out:
        from cc_balancer.cli_display import print_config_info

        print_config_info(config, "127.0.0.1", 8080, reload=True)
        output = fake_out.getvalue()

        # Check server info appears
        assert "127.0.0.1" in output
        assert "8080" in output

        # Check provider info appears
        assert "test-provider" in output
