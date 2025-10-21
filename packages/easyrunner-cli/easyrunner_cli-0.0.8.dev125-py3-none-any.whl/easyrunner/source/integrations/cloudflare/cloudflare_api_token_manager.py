"""Manages Cloudflare API tokens with secure storage.

This module provides core business logic for managing Cloudflare API tokens.
Depends on abstract SecretStore for storage, allowing different interfaces
(CLI, Web API, Web UI) to provide their own storage implementations.
"""

import logging
from typing import Optional

from ...store import SecretStore

logger = logging.getLogger(__name__)


class CloudflareApiTokenManager:
    """Manages Cloudflare API tokens with secure storage.

    Supports multiple Cloudflare accounts, each with their own API token.
    Uses a pluggable secret store implementation for secure storage.

    Note: This core implementation requires explicit SecretStore injection.
    CLI code typically injects KeyringSecretStore, while Web API/UI might
    inject database-backed implementations.

    Args:
        account_name: Name of the Cloudflare account (default: "default")
        secret_store: SecretStore implementation for secure storage (required)
    """

    def __init__(
        self, account_name: str = "default", secret_store: Optional[SecretStore] = None
    ) -> None:
        """Initialize manager for a specific Cloudflare account.

        Args:
            account_name: Name of the Cloudflare account (default: "default")
            secret_store: SecretStore implementation (required for core library)
        """
        if secret_store is None:
            raise ValueError(
                "secret_store is required. Core library does not provide default implementations. "
                "CLI code should inject KeyringSecretStore(), Web API/UI should inject their own implementation."
            )
        
        self.account_name = account_name
        self.secret_key = f"easyrunner/cloudflare/api_token/{account_name}"
        self.secret_store = secret_store

    def store_api_token(self, api_token: str) -> bool:
        """Store Cloudflare API token in secure storage.

        Args:
            api_token: The Cloudflare API token to store

        Returns:
            True if successful, False otherwise
        """
        success = self.secret_store.store_secret(self.secret_key, api_token)
        if success:
            logger.debug(f"Cloudflare API token stored for account: {self.account_name}")
        else:
            logger.error(f"Failed to store Cloudflare API token for account: {self.account_name}")
        return success

    def get_api_token(self) -> Optional[str]:
        """Retrieve Cloudflare API token from secure storage.

        Returns:
            The stored Cloudflare API token, or None if not found
        """
        token = self.secret_store.get_secret(self.secret_key)
        if token:
            logger.debug(f"Cloudflare API token retrieved for account: {self.account_name}")
        else:
            logger.debug(f"Cloudflare API token not found for account: {self.account_name}")
        return token

    def delete_api_token(self) -> bool:
        """Delete Cloudflare API token from secure storage.

        Returns:
            True if successful, False otherwise
        """
        success = self.secret_store.delete_secret(self.secret_key)
        if success:
            logger.debug(f"Cloudflare API token deleted for account: {self.account_name}")
        else:
            logger.error(f"Failed to delete Cloudflare API token for account: {self.account_name}")
        return success
