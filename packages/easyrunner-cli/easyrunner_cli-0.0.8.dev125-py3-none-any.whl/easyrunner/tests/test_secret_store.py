"""Tests for the SecretStore abstraction.

This test suite verifies that:
1. SecretStore is properly exported from easyrunner.source.store
2. SecretStore can be imported from the CLI integrations (backward compatibility)
3. The abstraction allows different implementations
"""

import pytest

from easyrunner.source.store import SecretStore


def test_secret_store_is_abstract():
    """SecretStore cannot be instantiated directly."""
    with pytest.raises(TypeError):
        SecretStore()


def test_secret_store_requires_store_secret():
    """Subclasses must implement store_secret method."""

    class IncompleteStore(SecretStore):
        def get_secret(self, key: str):
            pass

        def delete_secret(self, key: str):
            pass

    with pytest.raises(TypeError):
        IncompleteStore()


def test_secret_store_requires_get_secret():
    """Subclasses must implement get_secret method."""

    class IncompleteStore(SecretStore):
        def store_secret(self, key: str, value: str):
            pass

        def delete_secret(self, key: str):
            pass

    with pytest.raises(TypeError):
        IncompleteStore()


def test_secret_store_requires_delete_secret():
    """Subclasses must implement delete_secret method."""

    class IncompleteStore(SecretStore):
        def store_secret(self, key: str, value: str):
            pass

        def get_secret(self, key: str):
            pass

    with pytest.raises(TypeError):
        IncompleteStore()


class MockSecretStore(SecretStore):
    """A simple mock implementation for testing."""

    def __init__(self):
        self.secrets = {}

    def store_secret(self, key: str, value: str) -> bool:
        self.secrets[key] = value
        return True

    def get_secret(self, key: str):
        return self.secrets.get(key)

    def delete_secret(self, key: str) -> bool:
        if key in self.secrets:
            del self.secrets[key]
            return True
        return False


def test_concrete_implementation_works():
    """A concrete implementation can be created and used."""
    store = MockSecretStore()

    # Test store
    assert store.store_secret("test/key", "secret_value") is True

    # Test get
    assert store.get_secret("test/key") == "secret_value"

    # Test get non-existent
    assert store.get_secret("nonexistent") is None

    # Test delete
    assert store.delete_secret("test/key") is True
    assert store.get_secret("test/key") is None

    # Test delete non-existent
    assert store.delete_secret("nonexistent") is False


def test_integrations_moved_to_core():
    """Core integrations should be importable from core library."""
    # Test GitHub integration
    # Test Cloudflare integration
    from easyrunner.source.integrations.cloudflare import (
        CloudflareApiClient,
        CloudflareApiConfig,
        CloudflareApiTokenManager,
    )
    from easyrunner.source.integrations.github import (
        GitHubDeviceFlow,
        GitHubOAuthConfig,
        GitHubTokenManager,
    )

    # Test Hetzner integration
    from easyrunner.source.integrations.hetzner import HetznerApiKeyManager

    # All should be importable without errors
    assert GitHubTokenManager is not None
    assert GitHubDeviceFlow is not None
    assert GitHubOAuthConfig is not None
    assert CloudflareApiTokenManager is not None
    assert CloudflareApiClient is not None
    assert CloudflareApiConfig is not None
    assert HetznerApiKeyManager is not None


def test_integration_managers_require_secret_store():
    """Integration managers in core should work with injected SecretStore."""
    from easyrunner.source.integrations.cloudflare import CloudflareApiTokenManager
    from easyrunner.source.integrations.github import GitHubTokenManager
    from easyrunner.source.integrations.hetzner import HetznerApiKeyManager

    # Create mock secret store
    mock_store = MockSecretStore()

    # Should be able to instantiate with SecretStore
    github_manager = GitHubTokenManager(secret_store=mock_store)
    cloudflare_manager = CloudflareApiTokenManager(secret_store=mock_store)
    hetzner_manager = HetznerApiKeyManager(secret_store=mock_store)

    # All should use the same store instance
    assert github_manager.secret_store is mock_store
    assert cloudflare_manager.secret_store is mock_store
    assert hetzner_manager.secret_store is mock_store


def test_dependency_injection_pattern():
    """Test that SecretStore can be injected as a dependency."""

    class TokenManager:
        def __init__(self, secret_store: SecretStore):
            self.secret_store = secret_store

        def store_token(self, token: str) -> bool:
            return self.secret_store.store_secret("easyrunner/token", token)

        def get_token(self):
            return self.secret_store.get_secret("easyrunner/token")

    # Use mock implementation
    mock_store = MockSecretStore()
    manager = TokenManager(secret_store=mock_store)

    # Test dependency injection works
    assert manager.store_token("my_token") is True
    assert manager.get_token() == "my_token"

    # Use keyring implementation (if available)
    try:
        from easyrunner_cli.source.integrations import KeyringSecretStore

        keyring_store = KeyringSecretStore()
        manager2 = TokenManager(secret_store=keyring_store)

        # TokenManager works with any SecretStore implementation
        assert isinstance(manager2.secret_store, SecretStore)
    except ImportError:
        # Skip if CLI not available
        pass
