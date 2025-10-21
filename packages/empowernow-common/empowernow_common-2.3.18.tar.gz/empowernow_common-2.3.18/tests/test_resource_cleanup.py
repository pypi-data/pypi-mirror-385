"""Test resource cleanup for UnifiedTokenValidator."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from empowernow_common.jwt import (
    UnifiedTokenValidator,
    IdPConfig,
    ValidationStrategy,
    ConfigurationError,
    ValidationError,
)
from empowernow_common.jwt.config import IdPCatalogue


class TestUnifiedTokenValidatorCleanup:
    """Test proper resource cleanup for UnifiedTokenValidator."""

    def test_invalid_default_idp_raises_error(self):
        """Test that specifying non-existent default IdP raises ConfigurationError."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.for_name = Mock(return_value=None)
        catalogue.__len__ = Mock(return_value=1)

        with pytest.raises(ConfigurationError, match="Default IdP for opaque tokens not found: nonexistent"):
            UnifiedTokenValidator(catalogue, default_idp_for_opaque="nonexistent")

        # Verify for_name was called to validate
        catalogue.for_name.assert_called_with("nonexistent")

    def test_valid_default_idp_accepted(self):
        """Test that valid default IdP is accepted."""
        catalogue = Mock(spec=IdPCatalogue)
        idp_config = Mock(spec=IdPConfig)
        catalogue.for_name = Mock(return_value=idp_config)
        catalogue.__len__ = Mock(return_value=1)

        # Should not raise
        validator = UnifiedTokenValidator(catalogue, default_idp_for_opaque="valid")
        assert validator.default_idp_for_opaque == "valid"

    @pytest.mark.asyncio
    async def test_close_idempotency(self):
        """Test that close() can be called multiple times safely."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        validator = UnifiedTokenValidator(catalogue)

        # Create mock HTTP client
        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        validator._http_client = mock_client

        # First close
        await validator.close()
        assert validator._closed is True
        mock_client.aclose.assert_called_once()
        assert validator._http_client is None  # Should be cleared

        # Second close should be no-op
        await validator.close()
        # Still only called once
        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_cleans_up_validators(self):
        """Test that close() properly cleans up validators."""
        from empowernow_common.jwt.validators import IntrospectionValidator

        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        validator = UnifiedTokenValidator(catalogue)

        # Create mock validators
        mock_introspection = AsyncMock(spec=IntrospectionValidator)
        mock_introspection.close = AsyncMock()

        validator._validators = {
            "idp1": mock_introspection,
            "idp2": Mock()  # Not an IntrospectionValidator
        }
        validator._validator_access_order = ["idp1", "idp2"]

        # Create mock HTTP client
        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        validator._http_client = mock_client

        await validator.close()

        # Check introspection validator was closed
        mock_introspection.close.assert_called_once()

        # Check collections cleared
        assert len(validator._validators) == 0
        assert len(validator._validator_access_order) == 0

        # Check HTTP client closed
        mock_client.aclose.assert_called_once()
        assert validator._http_client is None
        assert validator._closed is True

    @pytest.mark.asyncio
    async def test_operations_after_close_raise_error(self):
        """Test that operations after close raise ValidationError."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        validator = UnifiedTokenValidator(catalogue)
        await validator.close()

        # Create mock IdP config
        idp_config = Mock(spec=IdPConfig)
        idp_config.name = "test-idp"

        # Attempting to get validator after close should raise
        with pytest.raises(ValidationError, match="UnifiedTokenValidator is closed"):
            await validator._get_validator(idp_config)

    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test async context manager properly closes resources."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        mock_client = None
        # Use context manager
        async with UnifiedTokenValidator(catalogue) as validator:
            # Create mock HTTP client
            mock_client = AsyncMock()
            mock_client.aclose = AsyncMock()
            validator._http_client = mock_client

            assert validator._closed is False

        # After exiting context, should be closed
        assert validator._closed is True
        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_with_exception(self):
        """Test context manager closes even when exception occurs."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        mock_client = None
        validator_ref = None
        with pytest.raises(ValueError):
            async with UnifiedTokenValidator(catalogue) as validator:
                validator_ref = validator
                mock_client = AsyncMock()
                mock_client.aclose = AsyncMock()
                validator._http_client = mock_client
                raise ValueError("Test exception")

        # Should still be closed despite exception
        assert validator_ref._closed is True
        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_handles_validator_close_errors(self):
        """Test that close continues even if validator close fails."""
        from empowernow_common.jwt.validators import IntrospectionValidator

        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        validator = UnifiedTokenValidator(catalogue)

        # Create mock validator that raises on close
        mock_introspection = AsyncMock(spec=IntrospectionValidator)
        mock_introspection.close = AsyncMock(side_effect=Exception("Close failed"))

        validator._validators = {"idp1": mock_introspection}
        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        validator._http_client = mock_client

        # Should not raise, but should log error
        await validator.close()

        # Check everything still cleaned up
        assert len(validator._validators) == 0
        assert validator._closed is True
        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_thread_safe_validator_creation(self):
        """Test that validator creation is thread-safe."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        validator = UnifiedTokenValidator(catalogue)

        # Create IdP configs
        idp1 = Mock(spec=IdPConfig)
        idp1.name = "idp1"
        idp1.strategy = ValidationStrategy.JWKS
        idp1.issuer = "https://idp1.example.com"

        idp2 = Mock(spec=IdPConfig)
        idp2.name = "idp2"
        idp2.strategy = ValidationStrategy.JWKS
        idp2.issuer = "https://idp2.example.com"

        # Mock JWKSValidator creation
        with patch('empowernow_common.jwt.validators.JWKSValidator') as mock_jwks:
            mock_jwks.return_value = Mock()

            # Simulate concurrent access
            async def get_validator1():
                return await validator._get_validator(idp1)

            async def get_validator2():
                return await validator._get_validator(idp2)

            # Run concurrently
            results = await asyncio.gather(get_validator1(), get_validator2())

            # Both should succeed
            assert len(results) == 2
            assert "idp1" in validator._validators
            assert "idp2" in validator._validators

    def test_destructor_warning(self):
        """Test that destructor warns about unclosed resources."""
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.__len__ = Mock(return_value=1)

        with patch('empowernow_common.jwt.validators.logger') as mock_logger:
            validator = UnifiedTokenValidator(catalogue)
            validator._http_client = Mock()  # Simulate having an HTTP client

            # Trigger destructor
            del validator

            # Check warning was logged
            mock_logger.warning.assert_called_with(
                "UnifiedTokenValidator not properly closed. "
                "Use 'await validator.close()' or async context manager."
            )