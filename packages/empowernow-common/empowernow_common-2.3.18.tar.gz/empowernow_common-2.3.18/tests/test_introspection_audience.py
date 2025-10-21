"""Test audience validation in introspection."""

import pytest
from unittest.mock import AsyncMock, patch

from empowernow_common.jwt.config import IdPConfig, IntrospectionConfig, ValidationStrategy
from empowernow_common.jwt.validators import IntrospectionValidator
from empowernow_common.jwt.errors import AudienceMismatchError


class TestIntrospectionAudienceValidation:
    """Test that introspection validator properly validates audiences."""

    async def test_valid_audience_single_string(self):
        """Test introspection with valid audience as single string."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            audience=["api://test-audience", "api://another-audience"],
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )

        validator = IntrospectionValidator(idp_config)

        with patch.object(validator._oauth_client, 'introspect_token') as mock_introspect:
            mock_introspect.return_value = {
                "active": True,
                "aud": "api://test-audience",  # Matches one of our audiences
                "sub": "user123",
                "exp": 9999999999
            }
            result = await validator.validate_token("valid-token")
            assert result["raw"]["aud"] == "api://test-audience"

    async def test_valid_audience_array(self):
        """Test introspection with valid audience as array."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            audience=["api://test-audience", "api://another-audience"],
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )

        validator = IntrospectionValidator(idp_config)

        with patch.object(validator._oauth_client, 'introspect_token') as mock_introspect:
            mock_introspect.return_value = {
                "active": True,
                "aud": ["api://another-audience", "api://third"],  # One matches
                "sub": "user123",
                "exp": 9999999999
            }
            result = await validator.validate_token("valid-token")
            assert "api://another-audience" in result["raw"]["aud"]

    async def test_invalid_audience(self):
        """Test introspection rejects invalid audience."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            audience=["api://test-audience", "api://another-audience"],
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )

        validator = IntrospectionValidator(idp_config)

        with patch.object(validator._oauth_client, 'introspect_token') as mock_introspect:
            mock_introspect.return_value = {
                "active": True,
                "aud": "api://wrong-audience",  # Doesn't match
                "sub": "user123",
                "exp": 9999999999
            }
            with pytest.raises(AudienceMismatchError, match="Token audience doesn't match"):
                await validator.validate_token("invalid-audience-token")

    async def test_missing_audience_in_response(self):
        """Test introspection rejects when audience is missing from response."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            audience=["api://test-audience"],
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )

        validator = IntrospectionValidator(idp_config)

        with patch.object(validator._oauth_client, 'introspect_token') as mock_introspect:
            mock_introspect.return_value = {
                "active": True,
                "sub": "user123",
                "exp": 9999999999
                # No "aud" field
            }
            with pytest.raises(AudienceMismatchError, match="No audience in introspection response"):
                await validator.validate_token("no-audience-token")

    async def test_no_audience_configured(self):
        """Test introspection accepts any audience when none configured."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            # No audience configured - validation is optional
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )

        validator = IntrospectionValidator(idp_config)

        with patch.object(validator._oauth_client, 'introspect_token') as mock_introspect:
            mock_introspect.return_value = {
                "active": True,
                "aud": "any-audience",  # Any audience is OK when not configured
                "sub": "user123",
                "exp": 9999999999
            }
            result = await validator.validate_token("any-token")
            assert result["raw"]["aud"] == "any-audience"

    async def test_audience_as_single_string_config(self):
        """Test IdP configured with single audience string."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            audience="api://single-audience",  # Single string, not array
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )

        validator = IntrospectionValidator(idp_config)

        with patch.object(validator._oauth_client, 'introspect_token') as mock_introspect:
            mock_introspect.return_value = {
                "active": True,
                "aud": "api://single-audience",
                "sub": "user123",
                "exp": 9999999999
            }
            result = await validator.validate_token("valid-token")
            assert result["raw"]["aud"] == "api://single-audience"