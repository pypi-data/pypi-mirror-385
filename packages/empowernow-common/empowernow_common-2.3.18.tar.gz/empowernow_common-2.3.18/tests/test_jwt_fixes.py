"""Tests for JWT validation fixes and enhancements."""

import pytest
import asyncio
import time
import json
import httpx
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from empowernow_common.jwt import (
    JWKSValidator,
    IntrospectionValidator,
    UnifiedTokenValidator,
    IdPConfig,
    JWKSConfig,
    IntrospectionConfig,
    ValidationStrategy,
    IdPCatalogue,
    ValidationError,
    NetworkError,
    DiscoveryError,
    JWKSFetchError,
    IntrospectionError,
)
from empowernow_common.jwt.lightweight_validator import LightweightValidator, ValidationError as LightweightValidationError
from empowernow_common.fastapi import build_auth_dependency
from empowernow_common.identity import UniqueIdentity
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials


class TestJWKSDiscovery:
    """Test OIDC discovery implementation."""

    @pytest.mark.asyncio
    async def test_jwks_discovery_success(self):
        """Test successful OIDC discovery."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://idp.example.com",
            strategy=ValidationStrategy.JWKS,
            jwks=JWKSConfig()
        )

        validator = JWKSValidator(idp_config)
        validator._http_client = AsyncMock()

        # Mock discovery response
        discovery_doc = {"jwks_uri": "https://idp.example.com/keys"}
        response = Mock()
        response.json.return_value = discovery_doc
        response.raise_for_status = Mock()
        validator._http_client.get.return_value = response

        # Mock discovery cache
        validator._shared_discovery_cache = Mock()
        validator._shared_discovery_cache.get.return_value = None

        jwks_url = await validator._get_jwks_url()

        assert jwks_url == "https://idp.example.com/keys"
        validator._http_client.get.assert_called_with(
            "https://idp.example.com/.well-known/openid-configuration"
        )
        validator._shared_discovery_cache.set.assert_called()

    @pytest.mark.asyncio
    async def test_jwks_discovery_fallback(self):
        """Test fallback to well-known location on discovery failure."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://idp.example.com",
            strategy=ValidationStrategy.JWKS,
            jwks=JWKSConfig()
        )

        validator = JWKSValidator(idp_config)
        validator._http_client = AsyncMock()
        validator._http_client.get.side_effect = Exception("Network error")
        validator._shared_discovery_cache = None

        jwks_url = await validator._get_jwks_url()

        assert jwks_url == "https://idp.example.com/.well-known/jwks.json"

    @pytest.mark.asyncio
    async def test_jwks_discovery_cache_hit(self):
        """Test JWKS discovery uses cache when available."""
        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://idp.example.com",
            strategy=ValidationStrategy.JWKS,
            jwks=JWKSConfig()
        )

        validator = JWKSValidator(idp_config)

        # Mock discovery cache with cached result
        validator._shared_discovery_cache = Mock()
        validator._shared_discovery_cache.get.return_value = {
            "jwks_uri": "https://idp.example.com/cached-keys"
        }

        jwks_url = await validator._get_jwks_url()

        assert jwks_url == "https://idp.example.com/cached-keys"
        # Should not make HTTP request when cache hit
        assert not hasattr(validator, '_http_client') or validator._http_client is None


class TestIntrospectionCacheTTL:
    """Test introspection cache TTL calculation."""

    @pytest.mark.asyncio
    @patch('empowernow_common.jwt.validators.hmac_token_key')
    async def test_cache_ttl_with_exp(self, mock_hmac):
        """Test TTL calculation when exp is present."""
        # Mock hmac_token_key to return a consistent value
        mock_hmac.return_value = "test-cache-key"

        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://idp.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            introspection=IntrospectionConfig(
                url="https://idp.example.com/introspect",
                client_id="test",
                client_secret="secret",
                cache_ttl_seconds=300  # 5 minutes configured
            )
        )

        validator = IntrospectionValidator(idp_config)

        # Use a mock that tracks the TTL passed to set
        cache_mock = Mock()
        ttl_holder = {"ttl": None}

        def capture_ttl(key, value, ttl):
            ttl_holder["ttl"] = ttl

        cache_mock.get = Mock(return_value=None)  # Simulate cache miss
        cache_mock.set = Mock(side_effect=capture_ttl)
        validator._cache = cache_mock

        # Mock introspection response with exp 2 minutes from now
        future_exp = int(time.time()) + 120
        result = {
            "active": True,
            "sub": "user123",
            "exp": future_exp,
            "iss": "https://idp.example.com"
        }

        # Mock OAuth client
        validator._oauth_client = AsyncMock()
        validator._oauth_client.introspect_token.return_value = result

        await validator.validate_token("test-token")

        # TTL should be min(300, max(30, 120 - 60)) = min(300, 60) = 60
        assert cache_mock.set.called
        assert ttl_holder["ttl"] == 60  # TTL should be 60 seconds

    @pytest.mark.asyncio
    @patch('empowernow_common.jwt.validators.hmac_token_key')
    async def test_cache_ttl_without_exp(self, mock_hmac):
        """Test TTL uses configured value when exp is absent."""
        # Mock hmac_token_key to return a consistent value
        mock_hmac.return_value = "test-cache-key"

        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://idp.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            introspection=IntrospectionConfig(
                url="https://idp.example.com/introspect",
                client_id="test",
                client_secret="secret",
                cache_ttl_seconds=180
            )
        )

        validator = IntrospectionValidator(idp_config)

        # Use a mock that tracks the TTL passed to set
        cache_mock = Mock()
        ttl_holder = {"ttl": None}

        def capture_ttl(key, value, ttl):
            ttl_holder["ttl"] = ttl

        cache_mock.get = Mock(return_value=None)  # Simulate cache miss
        cache_mock.set = Mock(side_effect=capture_ttl)
        validator._cache = cache_mock

        result = {
            "active": True,
            "sub": "user123",
            "iss": "https://idp.example.com"
        }

        validator._oauth_client = AsyncMock()
        validator._oauth_client.introspect_token.return_value = result

        await validator.validate_token("test-token")

        # Should use configured TTL
        assert cache_mock.set.called
        assert ttl_holder["ttl"] == 180

    @pytest.mark.asyncio
    @patch('empowernow_common.jwt.validators.hmac_token_key')
    async def test_cache_ttl_near_expiry(self, mock_hmac):
        """Test TTL minimum of 30 seconds when token near expiry."""
        # Mock hmac_token_key to return a consistent value
        mock_hmac.return_value = "test-cache-key"

        idp_config = IdPConfig(
            name="test-idp",
            issuer="https://idp.example.com",
            strategy=ValidationStrategy.INTROSPECTION,
            introspection=IntrospectionConfig(
                url="https://idp.example.com/introspect",
                client_id="test",
                client_secret="secret",
                cache_ttl_seconds=300
            )
        )

        validator = IntrospectionValidator(idp_config)

        # Use a mock that tracks the TTL passed to set
        cache_mock = Mock()
        ttl_holder = {"ttl": None}

        def capture_ttl(key, value, ttl):
            ttl_holder["ttl"] = ttl

        cache_mock.get = Mock(return_value=None)  # Simulate cache miss
        cache_mock.set = Mock(side_effect=capture_ttl)
        validator._cache = cache_mock

        # Token expires in 70 seconds
        future_exp = int(time.time()) + 70
        result = {
            "active": True,
            "sub": "user123",
            "exp": future_exp,
            "iss": "https://idp.example.com"
        }

        validator._oauth_client = AsyncMock()
        validator._oauth_client.introspect_token.return_value = result

        await validator.validate_token("test-token")

        # TTL should be min(300, max(30, 70 - 60)) = min(300, 30) = 30
        assert cache_mock.set.called
        assert ttl_holder["ttl"] == 30


class TestJWKSValidatorKidHandling:
    """Test JWKS validator kid-less key selection."""

    @pytest.mark.asyncio
    async def test_single_matching_key_succeeds(self):
        """Test selection succeeds with single matching candidate."""
        validator = LightweightValidator(
            jwks_url="https://idp.example.com/jwks",
            expected_audience="test-api"
        )

        # Mock JWKS with single RS256 key
        jwks_data = {
            "keys": [
                {"kty": "RSA", "alg": "RS256", "n": "test", "e": "AQAB"}
            ]
        }

        # Mock cache to return JWKS
        validator._jwks_cache = {f"jwks:https://idp.example.com/jwks": jwks_data}

        with patch.object(validator, '_jwk_to_pem', return_value="PEM"):
            key = await validator._get_public_key(
                key_id=None,
                jwks_url="https://idp.example.com/jwks",
                algorithm="RS256",
                http_client=Mock()
            )
            assert key == "PEM"

    @pytest.mark.asyncio
    async def test_multiple_matching_keys_fails(self):
        """Test selection fails with multiple matching candidates."""
        validator = LightweightValidator(
            jwks_url="https://idp.example.com/jwks",
            expected_audience="test-api"
        )

        # Mock JWKS with multiple RS256 keys
        jwks_data = {
            "keys": [
                {"kty": "RSA", "alg": "RS256", "n": "test1", "e": "AQAB"},
                {"kty": "RSA", "alg": "RS256", "n": "test2", "e": "AQAB"}
            ]
        }

        # Mock _fetch_jwks to return the test JWKS data (AsyncMock since it's async)
        with patch.object(validator, '_fetch_jwks', AsyncMock(return_value=jwks_data)):
            with pytest.raises(LightweightValidationError, match="Multiple keys match"):
                await validator._get_public_key(
                    key_id=None,
                    jwks_url="https://idp.example.com/jwks",
                    algorithm="RS256",
                    http_client=Mock()
                )

    @pytest.mark.asyncio
    async def test_no_matching_key_fails(self):
        """Test selection fails when no keys match algorithm."""
        validator = LightweightValidator(
            jwks_url="https://idp.example.com/jwks",
            expected_audience="test-api"
        )

        # Mock JWKS with ES256 key only
        jwks_data = {
            "keys": [
                {"kty": "EC", "alg": "ES256", "crv": "P-256", "x": "test", "y": "test"}
            ]
        }

        # Mock _fetch_jwks to return the test JWKS data (AsyncMock since it's async)
        with patch.object(validator, '_fetch_jwks', AsyncMock(return_value=jwks_data)):
            with pytest.raises(LightweightValidationError, match="No keys match algorithm"):
                await validator._get_public_key(
                    key_id=None,
                    jwks_url="https://idp.example.com/jwks",
                    algorithm="RS256",
                    http_client=Mock()
                )

    @pytest.mark.asyncio
    async def test_missing_kid_and_alg_fails(self):
        """Test selection fails when both kid and alg are missing."""
        validator = LightweightValidator(
            jwks_url="https://idp.example.com/jwks",
            expected_audience="test-api"
        )

        # Mock JWKS
        jwks_data = {
            "keys": [
                {"kty": "RSA", "n": "test", "e": "AQAB"}
            ]
        }

        # Mock _fetch_jwks to return the test JWKS data (AsyncMock since it's async)
        with patch.object(validator, '_fetch_jwks', AsyncMock(return_value=jwks_data)):
            with pytest.raises(LightweightValidationError, match="Token missing both kid and alg"):
                await validator._get_public_key(
                    key_id=None,
                    jwks_url="https://idp.example.com/jwks",
                    algorithm=None,
                    http_client=Mock()
                )


class TestFastAPIIntegration:
    """Test FastAPI dependency enhancements."""

    @pytest.mark.asyncio
    async def test_unique_id_added_to_claims(self):
        """Test unique_id is properly added to claims."""
        validator = AsyncMock()
        validator.validate_token.return_value = {
            "iss": "https://idp.example.com",
            "sub": "user123",
            "idp_name": "test-idp",
            "roles": ["admin"],
            "permissions": ["read", "write"]
        }

        auth_dep = build_auth_dependency(validator=validator)

        # Mock request and credentials
        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        claims = await auth_dep(request, creds)

        # Check unique_id was added
        assert "unique_id" in claims
        expected_unique_id = UniqueIdentity(
            issuer="https://idp.example.com",
            subject="user123",
            idp_name="test-idp"
        ).value
        assert claims["unique_id"] == expected_unique_id

    @pytest.mark.asyncio
    async def test_normalized_claims_on_request_state(self):
        """Test normalized_claims is set on request.state but not in returned claims."""
        validator = AsyncMock()
        validator.validate_token.return_value = {
            "iss": "https://idp.example.com",
            "sub": "user123",
            "idp_name": "test-idp",
            "roles": ["admin", "user"],
            "permissions": ["read", "write"]
        }

        auth_dep = build_auth_dependency(validator=validator)

        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        claims = await auth_dep(request, creds)

        # normalized_claims should NOT be in returned claims dict
        assert "normalized_claims" not in claims

        # But roles and permissions should be at top level
        assert claims["roles"] == ["admin", "user"]
        assert claims["permissions"] == ["read", "write"]

        # Check request.state.normalized_claims was set
        assert request.state.normalized_claims == {
            "roles": ["admin", "user"],
            "permissions": ["read", "write"]
        }

    @pytest.mark.asyncio
    async def test_error_mapping_network_502(self):
        """Test network errors return 502."""
        validator = AsyncMock()
        validator.validate_token.side_effect = NetworkError("Connection failed")

        auth_dep = build_auth_dependency(validator=validator)

        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        with pytest.raises(HTTPException) as exc_info:
            await auth_dep(request, creds)

        assert exc_info.value.status_code == 502
        assert "unavailable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_error_mapping_discovery_502(self):
        """Test discovery errors return 502."""
        validator = AsyncMock()
        validator.validate_token.side_effect = DiscoveryError("Discovery failed")

        auth_dep = build_auth_dependency(validator=validator)

        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        with pytest.raises(HTTPException) as exc_info:
            await auth_dep(request, creds)

        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_error_mapping_jwks_fetch_502(self):
        """Test JWKS fetch errors return 502."""
        validator = AsyncMock()
        validator.validate_token.side_effect = JWKSFetchError("JWKS fetch failed")

        auth_dep = build_auth_dependency(validator=validator)

        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        with pytest.raises(HTTPException) as exc_info:
            await auth_dep(request, creds)

        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_error_mapping_introspection_502(self):
        """Test introspection errors return 502."""
        validator = AsyncMock()
        validator.validate_token.side_effect = IntrospectionError("Introspection failed")

        auth_dep = build_auth_dependency(validator=validator)

        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        with pytest.raises(HTTPException) as exc_info:
            await auth_dep(request, creds)

        assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_unique_id_format(self):
        """Test unique_id format matches expected pattern."""
        validator = AsyncMock()
        validator.validate_token.return_value = {
            "iss": "https://idp.example.com",
            "sub": "user123",
            "idp_name": "test-idp",
            "roles": [],
            "permissions": []
        }

        auth_dep = build_auth_dependency(validator=validator)

        request = Mock(spec=Request)
        request.state = Mock()
        creds = Mock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "test-token"

        claims = await auth_dep(request, creds)

        # Verify format: auth:account:idp_name:subject
        assert claims["unique_id"] == "auth:account:test-idp:user123"

    @pytest.mark.asyncio
    async def test_development_mode_bypass(self):
        """Test ENABLE_AUTHENTICATION=0 bypasses validation."""
        auth_dep = build_auth_dependency(
            idps_yaml_path="/fake/path.yaml",
            enable_authentication=False  # Explicitly disable
        )

        request = Mock(spec=Request)
        request.state = Mock()
        creds = None  # No credentials

        claims = await auth_dep(request, creds)

        assert claims["sub"] == "anonymous"
        assert claims["unique_id"] == "auth:anon"
        assert claims["roles"] == []
        assert claims["permissions"] == []


class TestClaimsMapperIntegration:
    """Test ClaimsMapper runs without configuration."""

    @pytest.mark.asyncio
    @patch('empowernow_common.jwt.validators.peek_payload')
    async def test_claimsmapper_extracts_keycloak_roles(self, mock_peek):
        """Test ClaimsMapper extracts roles from Keycloak format without config."""
        from empowernow_common.jwt import UnifiedTokenValidator, IdPConfig, ValidationStrategy
        from empowernow_common.jwt.config import IdPCatalogue

        # Mock token parsing to return issuer
        mock_peek.return_value = {"iss": "https://keycloak.example.com"}

        # Create IdP config WITHOUT claims_mapping
        idp_config = IdPConfig(
            name="keycloak",
            issuer="https://keycloak.example.com",
            strategy=ValidationStrategy.JWKS,
            # NO claims_mapping configured
        )

        # Create catalogue with single IdP
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.for_issuer.return_value = idp_config
        catalogue.__len__ = Mock(return_value=1)

        # Create validator
        validator = UnifiedTokenValidator(catalogue)

        # Mock the individual validator
        mock_validator = AsyncMock()
        mock_validator.validate_token.return_value = {
            "iss": "https://keycloak.example.com",
            "sub": "user123",
            "realm_access": {
                "roles": ["admin", "user"]
            },
            "resource_access": {
                "account": {
                    "roles": ["manage-account", "view-profile"]
                }
            },
            "idp_name": "keycloak",
            "validation_method": "jwks",
            "raw": {}
        }

        # Inject mock validator
        validator._validators = {"keycloak": mock_validator}

        # Validate token
        result = await validator.validate_token("test.jwt.token")

        # ClaimsMapper should extract realm_access.roles even without configuration
        assert "admin" in result["roles"]
        assert "user" in result["roles"]
        # resource_access.*.roles are NOT extracted (no wildcard support)
        assert "manage-account" not in result["roles"]
        assert len(result["roles"]) == 2  # Only realm roles

    @pytest.mark.asyncio
    @patch('empowernow_common.jwt.validators.peek_payload')
    async def test_claimsmapper_extracts_azure_ad_groups(self, mock_peek):
        """Test ClaimsMapper extracts Azure AD groups without config."""
        from empowernow_common.jwt import UnifiedTokenValidator, IdPConfig, ValidationStrategy
        from empowernow_common.jwt.config import IdPCatalogue

        # Mock token parsing to return issuer
        mock_peek.return_value = {"iss": "https://login.microsoftonline.com/tenant-id"}

        # Create IdP config WITHOUT claims_mapping
        idp_config = IdPConfig(
            name="azure-ad",
            issuer="https://login.microsoftonline.com/tenant-id",
            strategy=ValidationStrategy.JWKS,
            # NO claims_mapping configured
        )

        # Create catalogue with single IdP
        catalogue = Mock(spec=IdPCatalogue)
        catalogue.for_issuer.return_value = idp_config
        catalogue.__len__ = Mock(return_value=1)

        # Create validator
        validator = UnifiedTokenValidator(catalogue)

        # Mock the individual validator with Azure AD token structure
        mock_validator = AsyncMock()
        mock_validator.validate_token.return_value = {
            "iss": "https://login.microsoftonline.com/tenant-id",
            "sub": "user456",
            "groups": ["Finance", "Accounting", "Managers"],  # Azure AD groups
            "wids": ["role-guid-1", "role-guid-2"],  # Azure AD role IDs
            "idp_name": "azure-ad",
            "validation_method": "jwks",
            "raw": {}
        }

        # Inject mock validator
        validator._validators = {"azure-ad": mock_validator}

        # Validate token
        result = await validator.validate_token("test.jwt.token")

        # ClaimsMapper should extract groups as roles without configuration
        assert "Finance" in result["roles"]
        assert "Accounting" in result["roles"]
        assert "Managers" in result["roles"]
        # wids (role IDs) should also be extracted
        assert "role-guid-1" in result["roles"]
        assert "role-guid-2" in result["roles"]