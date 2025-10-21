"""Cloudflare API integration for DNS management.

This module provides core business logic for Cloudflare integration.
All classes depend on abstract interfaces (SecretStore, HttpClient) rather
than concrete implementations, allowing different interfaces (CLI, Web API,
Web UI) to inject their own implementations.
"""

from .cloudflare_api_client import CloudflareApiClient
from .cloudflare_api_config import CloudflareApiConfig
from .cloudflare_api_token_manager import CloudflareApiTokenManager

__all__ = [
    "CloudflareApiClient",
    "CloudflareApiConfig",
    "CloudflareApiTokenManager",
]
