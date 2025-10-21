"""Hetzner Cloud integration for infrastructure management.

This module provides core business logic for Hetzner Cloud integration.
All classes depend on abstract interfaces (SecretStore) rather than concrete
implementations, allowing different interfaces (CLI, Web API, Web UI) to
inject their own implementations.
"""

from .hetzner_api_key_manager import HetznerApiKeyManager

__all__ = [
    "HetznerApiKeyManager",
]
