"""Manages Hetzner API keys with secure storage per project.

This module provides core business logic for managing Hetzner API keys.
Depends on abstract SecretStore for storage, allowing different interfaces
(CLI, Web API, Web UI) to provide their own storage implementations.
"""

import logging
from typing import Optional

from ...store import SecretStore

logger = logging.getLogger(__name__)


class HetznerApiKeyManager:
    """Manages Hetzner API keys with secure storage per project.

    Supports multiple Hetzner projects, each with their own API key.
    Uses a pluggable secret store implementation for secure storage.

    Note: This core implementation requires explicit SecretStore injection.
    CLI code typically injects KeyringSecretStore, while Web API/UI might
    inject database-backed implementations.

    Args:
        project_name: Name of the Hetzner project (default: "default")
        secret_store: SecretStore implementation for secure storage (required)
    """

    SERVICE_NAME = "easyrunner.hetzner"

    def __init__(
        self, project_name: str = "default", secret_store: Optional[SecretStore] = None
    ) -> None:
        """Initialize manager for a specific Hetzner project.

        Args:
            project_name: Name of the Hetzner project (default: "default")
            secret_store: SecretStore implementation (required for core library)
        """
        if secret_store is None:
            raise ValueError(
                "secret_store is required. Core library does not provide default implementations. "
                "CLI code should inject KeyringSecretStore(), Web API/UI should inject their own implementation."
            )
        
        self.project_name = project_name
        self.secret_key = f"easyrunner/hetzner/api_key/{project_name}"
        self.secret_store = secret_store

    def store_api_key(self, api_key: str) -> bool:
        """Store Hetzner API key in secure storage.

        Args:
            api_key: The Hetzner API key to store

        Returns:
            True if successful, False otherwise
        """
        success = self.secret_store.store_secret(self.secret_key, api_key)
        if success:
            logger.debug(f"Hetzner API key stored for project: {self.project_name}")
        else:
            logger.error(f"Failed to store Hetzner API key for project: {self.project_name}")
        return success

    def get_api_key(self) -> Optional[str]:
        """Retrieve Hetzner API key from secure storage.

        Returns:
            The stored Hetzner API key, or None if not found
        """
        api_key = self.secret_store.get_secret(self.secret_key)
        if api_key:
            logger.debug(f"Hetzner API key retrieved for project: {self.project_name}")
        else:
            logger.debug(f"Hetzner API key not found for project: {self.project_name}")
        return api_key

    def delete_api_key(self) -> bool:
        """Delete Hetzner API key from secure storage.

        Returns:
            True if successful, False otherwise
        """
        success = self.secret_store.delete_secret(self.secret_key)
        if success:
            logger.debug(f"Hetzner API key deleted for project: {self.project_name}")
        else:
            logger.error(f"Failed to delete Hetzner API key for project: {self.project_name}")
        return success
