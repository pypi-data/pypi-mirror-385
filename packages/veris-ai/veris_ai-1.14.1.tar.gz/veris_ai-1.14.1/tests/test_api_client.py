"""Tests for SimulatorAPIClient endpoint URL generation and configuration."""

import os
from unittest.mock import patch

import pytest

from veris_ai.api_client import SimulatorAPIClient, get_api_client, set_api_client_params


def test_tool_mock_endpoint_default():
    """Test that tool_mock_endpoint property returns correct URL with default base_url."""
    client = SimulatorAPIClient()
    endpoint = client.tool_mock_endpoint

    # Should use default base URL
    assert endpoint == "https://simulator.api.veris.ai/v3/tool_mock"


def test_tool_mock_endpoint_custom_base_url():
    """Test that tool_mock_endpoint uses cached base_url from constructor."""
    client = SimulatorAPIClient(base_url="https://custom.api.com")
    endpoint = client.tool_mock_endpoint

    assert endpoint == "https://custom.api.com/v3/tool_mock"


def test_tool_mock_endpoint_with_env_var():
    """Test that tool_mock_endpoint respects VERIS_API_URL environment variable."""
    with patch.dict(os.environ, {"VERIS_API_URL": "https://test.api.veris.ai"}):
        client = SimulatorAPIClient()
        endpoint = client.tool_mock_endpoint

        assert endpoint == "https://test.api.veris.ai/v3/tool_mock"


def test_log_tool_call_endpoint():
    """Test get_log_tool_call_endpoint generates correct URL."""
    client = SimulatorAPIClient(base_url="https://test.api.com")
    endpoint = client.get_log_tool_call_endpoint("session-123")

    assert endpoint == "https://test.api.com/v3/log_tool_call?session_id=session-123"


def test_log_tool_response_endpoint():
    """Test get_log_tool_response_endpoint generates correct URL."""
    client = SimulatorAPIClient(base_url="https://test.api.com")
    endpoint = client.get_log_tool_response_endpoint("session-456")

    assert endpoint == "https://test.api.com/v3/log_tool_response?session_id=session-456"


def test_base_url_without_protocol_behavior():
    """Test that base_url without protocol is treated as relative path by urljoin."""
    # Note: urljoin treats URLs without protocol as relative paths
    client = SimulatorAPIClient(base_url="api.example.com")
    endpoint = client.tool_mock_endpoint

    # urljoin treats "api.example.com" as a relative path, so result is just the path component
    assert endpoint == "v3/tool_mock"


def test_base_url_with_trailing_slash():
    """Test that base_url with trailing slash is handled correctly."""
    client = SimulatorAPIClient(base_url="https://test.api.com/")
    endpoint = client.tool_mock_endpoint

    # urljoin should handle trailing slash correctly
    assert endpoint == "https://test.api.com/v3/tool_mock"


def test_custom_timeout():
    """Test that custom timeout is set correctly."""
    client = SimulatorAPIClient(timeout=30.0)
    assert client._timeout == 30.0


def test_default_timeout():
    """Test that default timeout is used when not specified."""
    with patch.dict(os.environ, {"VERIS_MOCK_TIMEOUT": "120.0"}):
        client = SimulatorAPIClient()
        assert client._timeout == 120.0


def test_set_api_client_params():
    """Test that set_api_client_params reconfigures the global client."""
    # Get original client
    original_client = get_api_client()
    original_endpoint = original_client.tool_mock_endpoint

    # Reconfigure with custom parameters
    set_api_client_params(base_url="https://custom.test.api", timeout=60.0)

    # Get new client and verify it's been updated
    new_client = get_api_client()
    assert new_client.tool_mock_endpoint == "https://custom.test.api/v3/tool_mock"
    assert new_client._timeout == 60.0

    # Restore original client
    set_api_client_params()


def test_set_api_client_params_partial():
    """Test that set_api_client_params can set only base_url or timeout."""
    # Set only base_url
    set_api_client_params(base_url="https://partial.test")
    client = get_api_client()
    assert client.tool_mock_endpoint == "https://partial.test/v3/tool_mock"
    assert client._timeout == 300  # Should use default

    # Set only timeout
    set_api_client_params(timeout=45.0)
    client = get_api_client()
    assert client._timeout == 45.0

    # Restore defaults
    set_api_client_params()


def test_multiple_endpoint_calls_use_cached_base_url():
    """Test that multiple endpoint property accesses use the same cached base_url."""
    client = SimulatorAPIClient(base_url="https://cached.api")

    # Call multiple endpoint methods
    endpoint1 = client.tool_mock_endpoint
    endpoint2 = client.get_log_tool_call_endpoint("session-1")
    endpoint3 = client.get_log_tool_response_endpoint("session-2")

    # All should use the same base URL
    assert endpoint1.startswith("https://cached.api/")
    assert endpoint2.startswith("https://cached.api/")
    assert endpoint3.startswith("https://cached.api/")


def test_empty_env_var_uses_default():
    """Test that empty VERIS_API_URL falls back to default."""
    with patch.dict(os.environ, {"VERIS_API_URL": ""}, clear=True):
        client = SimulatorAPIClient()
        # Empty string should NOT be used, should fall back to default
        assert client._get_base_url() == "https://simulator.api.veris.ai"
