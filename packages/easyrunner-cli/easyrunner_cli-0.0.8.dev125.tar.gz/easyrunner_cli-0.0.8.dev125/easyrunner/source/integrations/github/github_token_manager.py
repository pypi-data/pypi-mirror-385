"""Manages GitHub OAuth tokens with secure storage.

This module is part of the core library and can be used by CLI, Web API, and Web UI.
SecretStore must be injected - no default implementation to avoid coupling to
platform-specific storage.
"""

import logging
from typing import Optional

from ...store import SecretStore

logger = logging.getLogger(__name__)


class GitHubTokenManager:
    """Manages GitHub OAuth tokens with secure storage.

    Tokens are stored securely using a pluggable secret store implementation.
    Different interfaces can provide different SecretStore implementations:
    - CLI: KeyringSecretStore (macOS Keychain)
    - Web API: EnvironmentSecretStore or DatabaseSecretStore
    - Web UI: SessionSecretStore

    Note: SecretStore MUST be provided - no default implementation in core.
    """

    SECRET_KEY = "easyrunner/github/oauth_token"

    def __init__(self, secret_store: SecretStore) -> None:
        """Initialize token manager with a secret store.

        Args:
            secret_store: SecretStore implementation (REQUIRED).
                         CLI provides KeyringSecretStore,
                         Web API provides EnvironmentSecretStore, etc.
        """
        self.secret_store = secret_store

    def store_token(self, token: str) -> bool:
        """Store GitHub token in secure storage.

        Args:
            token: The GitHub OAuth token to store

        Returns:
            True if successful, False otherwise
        """
        success = self.secret_store.store_secret(self.SECRET_KEY, token)
        if success:
            logger.debug("GitHub token stored successfully")
        else:
            logger.error("Failed to store GitHub token")
        return success

    def get_token(self) -> Optional[str]:
        """Retrieve GitHub token from secure storage.

        Returns:
            The stored GitHub token, or None if not found
        """
        token = self.secret_store.get_secret(self.SECRET_KEY)
        if token:
            logger.debug("GitHub token retrieved successfully")
        else:
            logger.debug("GitHub token not found in storage")
        return token

    def delete_token(self) -> bool:
        """Delete GitHub token from secure storage.

        Returns:
            True if successful, False otherwise
        """
        success = self.secret_store.delete_secret(self.SECRET_KEY)
        if success:
            logger.debug("GitHub token deleted successfully")
        else:
            logger.error("Failed to delete GitHub token")
        return success
