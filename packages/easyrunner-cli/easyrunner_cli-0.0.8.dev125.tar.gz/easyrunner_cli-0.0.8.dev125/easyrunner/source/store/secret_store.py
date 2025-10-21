"""Abstract interface for secure secret storage.

This module defines the SecretStore abstraction that enables different secret
storage implementations across different deployment contexts:

MULTI-INTERFACE SUPPORT
=======================

Different interfaces can provide different implementations:

1. **CLI (easyrunner_cli)**:
   - Implementation: KeyringSecretStore
   - Location: easyrunner_cli/source/integrations/secret_store/
   - Storage: macOS Keyring (with Security Framework password challenges)
   - Use case: Local developer machine with platform-specific security

2. **Web API (future)**:
   - Possible implementations: EnvironmentSecretStore, DatabaseSecretStore, VaultSecretStore
   - Storage: Environment variables, database, or HashiCorp Vault
   - Use case: Server deployment with centralized secret management

3. **Web UI (future)**:
   - Possible implementations: SessionSecretStore
   - Storage: Session-based encryption
   - Use case: Browser-based access with ephemeral credentials

DESIGN PATTERN
==============

The core library depends on this abstract interface. Concrete implementations
are provided by the specific interface (CLI, Web API, etc) that use the core:

    Core Library
    │
    └─ depends on: SecretStore (abstract)
    
    CLI Layer
    ├─ provides: KeyringSecretStore implementation
    └─ injects into: GitHubTokenManager, CloudflareApiTokenManager, etc.
    
    Web API Layer
    ├─ provides: EnvironmentSecretStore or DatabaseSecretStore
    └─ injects same managers with different implementation

This enables:
- ✅ No business logic duplication
- ✅ Consistent behavior across all interfaces
- ✅ Easy to test with mock implementations
- ✅ Platform-specific security for each deployment

USAGE EXAMPLE
=============

In the core library:
    from easyrunner.source.store import SecretStore
    
    class GitHubTokenManager:
        def __init__(self, secret_store: SecretStore):
            self.secret_store = secret_store  # Abstract - can be any implementation

In the CLI:
    from easyrunner_cli.source.integrations import KeyringSecretStore
    
    secret_store = KeyringSecretStore()  # Concrete implementation
    manager = GitHubTokenManager(secret_store=secret_store)

In a Web API:
    from web_api.integrations import EnvironmentSecretStore
    
    secret_store = EnvironmentSecretStore()  # Different implementation
    manager = GitHubTokenManager(secret_store=secret_store)  # Same interface!

KEY DESIGN DECISIONS
====================

1. Path-based keys (e.g., "easyrunner/github/oauth_token"):
   - Allows hierarchical organization
   - Enables easier secret rotation and management
   - Consistent across all implementations

2. Store/get/delete interface:
   - Minimal and focused
   - No complex operations - just basic CRUD
   - Easy to implement in any backend

3. No exceptions, only return values:
   - Return False on failure instead of raising exceptions
   - Allows graceful degradation
   - Compatible with different error handling strategies

REFERENCE
=========

See ARCHITECTURE_REVIEW.md for full refactoring context.
"""

from abc import ABC, abstractmethod
from typing import Optional


class SecretStore(ABC):
    """Abstract interface for storing and retrieving secrets securely.

    Uses path-based keys for organization, allowing implementations to
    map to various backends (system keychains, vaults, databases, etc).

    Examples of key paths:
        - easyrunner/github/oauth_token
        - easyrunner/hetzner/api_key/project-name
        - easyrunner/cloudflare/api_token/account-name

    This abstraction enables different storage strategies for different
    deployment contexts without coupling the core library to any specific
    backend technology.
    """

    @abstractmethod
    def store_secret(self, key: str, value: str) -> bool:
        """Store a secret in secure storage.

        Args:
            key: Path-based key for the secret (e.g., "easyrunner/github/oauth_token")
            value: The secret value to store

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret from secure storage.

        Args:
            key: Path-based key for the secret

        Returns:
            The secret value if found, None otherwise
        """
        pass

    @abstractmethod
    def delete_secret(self, key: str) -> bool:
        """Delete a secret from secure storage.

        Args:
            key: Path-based key for the secret

        Returns:
            True if successful, False otherwise
        """
        pass
