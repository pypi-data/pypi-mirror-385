"""
Basic unit tests for the unified token validator.

These tests verify the core functionality of the new validation system.
"""

import pytest
import time
import json
import base64
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from empowernow_common.jwt import (
    ValidationStrategy,
    JWKSConfig,
    IntrospectionConfig,
    IdPConfig,
    UnknownIssuerError,
    TokenExpiredError,
    IntrospectionRejectedError,
    canonicalize_issuer,
    hmac_token_key,
    LRUTTLCache,
    peek_payload,
)


class TestConfiguration:
    """Test configuration dataclasses."""
    
    def test_jwks_config_defaults(self):
        """Test JWKS config with defaults."""
        config = JWKSConfig()
        assert config.enforce_issuer is True
        assert config.leeway_seconds == 60
        assert config.accept_id_tokens is False
        assert "RS256" in config.expected_algs
    
    def test_introspection_config_validation(self):
        """Test introspection config validation."""
        # Valid config
        config = IntrospectionConfig(
            url="https://idp.example.com/introspect",
            client_id="test-client",
            client_secret="secret"
        )
        assert config.cache_ttl_seconds == 0
        assert config.timeout_seconds == 5.0
        
        # Invalid config - missing URL
        with pytest.raises(ValueError, match="Introspection URL is required"):
            IntrospectionConfig(url="", client_id="test", client_secret="secret")
    
    def test_idp_config_strategy_inference(self):
        """Test IdP config strategy inference from legacy format."""
        # Legacy introspection config
        legacy = {
            "name": "test",
            "issuer": "https://test.example.com",
            "introspection_url": "https://test.example.com/introspect",
            "client_id": "client",
            "client_secret": "secret"
        }
        
        config = IdPConfig.from_legacy(legacy)
        assert config.strategy == ValidationStrategy.INTROSPECTION
        assert config.introspection is not None
        assert config.jwks is None
        
        # Legacy JWKS config (no introspection URL)
        legacy_jwks = {
            "name": "test",
            "issuer": "https://test.example.com",
            "audience": "api://test"  # Legacy had single audience, not audiences list
        }
        
        config_jwks = IdPConfig.from_legacy(legacy_jwks)
        assert config_jwks.strategy == ValidationStrategy.JWKS
        assert config_jwks.jwks is not None
        assert config_jwks.introspection is None


class TestUtils:
    """Test utility functions."""
    
    def test_canonicalize_issuer(self):
        """Test issuer canonicalization."""
        assert canonicalize_issuer("https://idp.example.com/") == "https://idp.example.com"
        assert canonicalize_issuer("https://idp.example.com") == "https://idp.example.com"
        assert canonicalize_issuer("") == ""
        assert canonicalize_issuer(None) == None
    
    def test_hmac_token_key(self):
        """Test HMAC token key generation."""
        token1 = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.sig"
        token2 = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJvdGhlciJ9.sig"
        
        key1 = hmac_token_key(token1)
        key2 = hmac_token_key(token2)
        
        # Keys should be different for different tokens
        assert key1 != key2
        
        # Same token should produce same key
        assert hmac_token_key(token1) == key1
    
    def test_lru_ttl_cache(self):
        """Test LRU cache with TTL."""
        cache = LRUTTLCache(maxsize=2, default_ttl=1)
        
        # Set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # TTL expiration
        cache.set("key2", "value2", ttl=0)  # Expires immediately
        time.sleep(0.1)
        assert cache.get("key2") is None
        
        # LRU eviction
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        assert cache.size() == 2
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestErrorHierarchy:
    """Test error hierarchy and semantics."""
    
    def test_error_stages(self):
        """Test that errors have proper stages."""
        err = UnknownIssuerError("Unknown issuer", issuer="https://unknown.com")
        assert err.stage == "routing"
        assert err.issuer == "https://unknown.com"
        
        err = TokenExpiredError()
        assert err.stage == "validation"
        
        err = IntrospectionRejectedError()
        assert err.stage == "introspection"


def create_mock_jwt(payload: Dict[str, Any], header: Dict[str, Any] = None) -> str:
    """Create a mock JWT token for testing."""
    if header is None:
        header = {"alg": "RS256", "typ": "JWT", "kid": "test-key"}
    
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip("=")
    
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip("=")
    
    # Mock signature
    signature = "mock_signature"
    
    return f"{header_b64}.{payload_b64}.{signature}"


class TestTokenPeeking:
    """Test token peeking without validation."""
    
    def test_peek_payload(self):
        """Test peeking at JWT payload."""
        token = create_mock_jwt({
            "sub": "user123",
            "iss": "https://idp.example.com",
            "exp": int(time.time()) + 3600,
            "scope": "read write"
        })
        
        payload = peek_payload(token)
        assert payload["sub"] == "user123"
        assert payload["iss"] == "https://idp.example.com"
        assert "exp" in payload
        assert payload["scope"] == "read write"
    
    def test_peek_invalid_token(self):
        """Test peeking at invalid token."""
        with pytest.raises(ValueError, match="invalid JWT"):
            peek_payload("not.a.token")
        
        with pytest.raises(ValueError, match="invalid JWT"):
            peek_payload("")


@pytest.mark.asyncio
class TestValidatorIntegration:
    """Integration tests for validators (with mocking)."""
    
    async def test_jwks_validator_success(self):
        """Test JWKS validator with successful validation."""
        # Create IdP config
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.JWKS,
            audience=["test-audience"],
            jwks=JWKSConfig(
                enforce_issuer=True,
            )
        )
        
        # Mock the LightweightValidator and HTTP client
        with patch("empowernow_common.jwt.validators.LightweightValidator") as MockValidator:
            mock_instance = MockValidator.return_value
            mock_instance.verify_jwt = AsyncMock(return_value={
                "sub": "user123",
                "iss": "https://test.example.com",
                "aud": "test-audience",
                "exp": int(time.time()) + 3600,
                "scp": ["read", "write"]
            })

            from empowernow_common.jwt.validators import JWKSValidator
            validator = JWKSValidator(idp_config)

            # JWKSValidator expects _http_client to be set by UnifiedTokenValidator
            # For standalone testing, we need to mock it
            mock_http_client = AsyncMock()
            validator._http_client = mock_http_client

            # Mock _get_jwks_url to avoid discovery call
            with patch.object(validator, '_get_jwks_url', return_value="https://test.example.com/.well-known/jwks.json"):
                token = create_mock_jwt({"sub": "user123"})
                claims = await validator.validate_token(token)
            
            assert claims["sub"] == "user123"
            assert claims["validation_method"] == "jwks"
            assert claims["idp_name"] == "test-idp"
            assert claims["scopes"] == ["read", "write"]
    
    async def test_introspection_validator_success(self):
        """Test introspection validator with successful validation."""
        # Create IdP config
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret",
                cache_ttl_seconds=30
            )
        )
        
        # Mock the HardenedOAuth client
        with patch("empowernow_common.jwt.validators.HardenedOAuth") as MockOAuth:
            mock_instance = MockOAuth.return_value
            mock_instance.introspect_token = AsyncMock(return_value={
                "active": True,
                "sub": "user123",
                "iss": "https://test.example.com",
                "scope": "read write",
                "exp": int(time.time()) + 3600
            })
            
            from empowernow_common.jwt.validators import IntrospectionValidator
            validator = IntrospectionValidator(idp_config)
            
            token = "opaque_token"
            claims = await validator.validate_token(token)
            
            assert claims["sub"] == "user123"
            assert claims["validation_method"] == "introspection"
            assert claims["idp_name"] == "test-idp"
            assert claims["scopes"] == ["read", "write"]
    
    async def test_introspection_validator_inactive_token(self):
        """Test introspection validator with inactive token."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://test.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            introspection=IntrospectionConfig(
                url="https://test.example.com/introspect",
                client_id="test-client",
                client_secret="secret"
            )
        )
        
        with patch("empowernow_common.jwt.validators.HardenedOAuth") as MockOAuth:
            mock_instance = MockOAuth.return_value
            mock_instance.introspect_token = AsyncMock(return_value={
                "active": False
            })
            
            from empowernow_common.jwt.validators import IntrospectionValidator
            validator = IntrospectionValidator(idp_config)
            
            with pytest.raises(IntrospectionRejectedError, match="Token is inactive"):
                await validator.validate_token("expired_token")


    async def test_validator_lifecycle_management(self):
        """Test validator LRU eviction with max_validators limit."""
        from empowernow_common.jwt.validators import UnifiedTokenValidator
        from empowernow_common.jwt import IdPCatalogue
        
        # Mock IdPCatalogue with __len__ method
        mock_catalogue = Mock(spec=IdPCatalogue)
        mock_catalogue.__len__ = Mock(return_value=3)  # Mock the len() call
        
        # Create unified validator with small limit for testing
        validator = UnifiedTokenValidator(mock_catalogue)
        validator._max_validators = 2  # Set small limit for testing
        
        # Create mock IdP configs
        idp1 = IdPConfig(
            name="idp1",
            issuer="https://idp1.example.com",
            strategy=ValidationStrategy.JWKS,
            jwks=JWKSConfig()
        )
        idp2 = IdPConfig(
            name="idp2",
            issuer="https://idp2.example.com",
            strategy=ValidationStrategy.JWKS,
            jwks=JWKSConfig()
        )
        idp3 = IdPConfig(
            name="idp3",
            issuer="https://idp3.example.com",
            strategy=ValidationStrategy.JWKS,
            jwks=JWKSConfig()
        )
        
        # Create validators for idp1 and idp2
        with patch("empowernow_common.jwt.validators.JWKSValidator"):
            v1 = await validator._get_validator(idp1)
            assert len(validator._validators) == 1
            assert "idp1" in validator._validators
            
            v2 = await validator._get_validator(idp2)
            assert len(validator._validators) == 2
            assert "idp2" in validator._validators
            
            # Creating validator for idp3 should evict idp1 (LRU)
            v3 = await validator._get_validator(idp3)
            assert len(validator._validators) == 2
            assert "idp1" not in validator._validators  # Evicted
            assert "idp2" in validator._validators
            assert "idp3" in validator._validators
            
            # Access idp2, then create idp1 again - should evict idp3
            v2_again = await validator._get_validator(idp2)
            v1_again = await validator._get_validator(idp1)
            assert len(validator._validators) == 2
            assert "idp3" not in validator._validators  # Evicted
            assert "idp1" in validator._validators
            assert "idp2" in validator._validators


if __name__ == "__main__":
    pytest.main([__file__, "-v"])