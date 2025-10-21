"""Tests for AISentinel Python SDK."""
import pytest
from unittest.mock import Mock, patch

from aisentinel import Governor
from aisentinel.config import SDKConfig


class TestGovernor:
    """Test the Governor class."""

    def test_initialization(self):
        """Test governor initialization with minimal config."""
        with patch("aisentinel.governor.requests.Session") as mock_session:
            governor = Governor(base_url="https://test.com", token="test-token")

            assert governor.base_url == "https://test.com"
            assert governor.config.token == "test-token"
            mock_session.assert_called_once()

    def test_preflight_allowed(self):
        """Test successful preflight check."""
        mock_response = Mock()
        mock_response.json.return_value = {"allowed": True, "reasons": []}

        with patch("aisentinel.governor.requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.post.return_value = mock_response
            mock_session.headers = {}
            mock_session_class.return_value = mock_session

            governor = Governor(base_url="https://test.com", token="test-token")

            candidate = {"tool": "test", "args": {}}
            state = {}

            result = governor.preflight(candidate, state)

            assert result["allowed"] is True
            mock_session.post.assert_called_once()

    def test_preflight_blocked(self):
        """Test blocked preflight check."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "allowed": False,
            "reasons": ["Policy violation"],
            "alternatives": []
        }

        with patch("aisentinel.governor.requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.post.return_value = mock_response
            mock_session.headers = {}
            mock_session_class.return_value = mock_session

            governor = Governor(base_url="https://test.com", token="test-token")

            candidate = {"tool": "test", "args": {}}
            state = {}

            result = governor.preflight(candidate, state)

            assert result["allowed"] is False
            assert "Policy violation" in result["reasons"]


class TestSDKConfig:
    """Test the SDKConfig class."""

    def test_load_defaults(self):
        """Test loading default configuration."""
        config = SDKConfig.load()

        assert config.base_url == "https://api.aisentinel.ai"
        assert config.offline_mode_enabled is True
        assert config.cache_ttl_seconds == 300

    def test_load_with_overrides(self):
        """Test loading configuration with overrides."""
        config = SDKConfig.load(overrides={
            "base_url": "https://custom.api.com",
            "token": "custom-token",
            "cache_ttl_seconds": 600
        })

        assert config.base_url == "https://custom.api.com"
        assert config.token == "custom-token"
        assert config.cache_ttl_seconds == 600
