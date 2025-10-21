"""Test IdPConfig audience handling."""

import pytest
from empowernow_common.jwt.config import IdPConfig, ValidationStrategy


class TestIdPConfigAudience:
    """Test IdPConfig.get_audience_list() method."""

    def test_audience_none(self):
        """Test when audience is None."""
        config = IdPConfig(
            name="test",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.JWKS,
            audience=None
        )
        assert config.get_audience_list() == []

    def test_audience_single_string(self):
        """Test when audience is a single string."""
        config = IdPConfig(
            name="test",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.JWKS,
            audience="api://single"
        )
        assert config.get_audience_list() == ["api://single"]

    def test_audience_list(self):
        """Test when audience is a list."""
        config = IdPConfig(
            name="test",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.JWKS,
            audience=["api://first", "api://second"]
        )
        assert config.get_audience_list() == ["api://first", "api://second"]

    def test_audience_empty_list(self):
        """Test when audience is an empty list."""
        config = IdPConfig(
            name="test",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.JWKS,
            audience=[]
        )
        assert config.get_audience_list() == []

    def test_from_legacy_with_audience(self):
        """Test from_legacy preserves audience field."""
        legacy = {
            "name": "test",
            "issuer": "https://test.example.com",
            "audience": "api://legacy"
        }
        config = IdPConfig.from_legacy(legacy)
        assert config.audience == "api://legacy"
        assert config.get_audience_list() == ["api://legacy"]

    def test_modern_config_with_audience(self):
        """Test modern config format with root-level audience."""
        modern = {
            "name": "test",
            "issuer": "https://test.example.com",
            "strategy": "INTROSPECTION",
            "audience": ["api://modern1", "api://modern2"],
            "introspection": {
                "url": "https://test.example.com/introspect",
                "client_id": "client",
                "client_secret": "secret"
            }
        }
        config = IdPConfig.from_legacy(modern)  # from_legacy handles both
        assert config.audience == ["api://modern1", "api://modern2"]
        assert config.get_audience_list() == ["api://modern1", "api://modern2"]