"""EasyRunner CLI integrations.

This module re-exports core integration classes and provides CLI-specific
implementations like KeyringSecretStore. CLI code should import from here
rather than directly from core to maintain a clear interface boundary.
"""

# Re-export core integration classes
from easyrunner.source.integrations.cloudflare import (
    CloudflareApiClient,
    CloudflareApiConfig,
    CloudflareApiTokenManager,
)
from easyrunner.source.integrations.github import (
    DeviceCodeResponse,
    GitHubDeviceFlow,
    GitHubOAuthConfig,
    GitHubTokenManager,
)
from easyrunner.source.integrations.hetzner import HetznerApiKeyManager

# Re-export SecretStore from core and CLI-specific implementation
from .secret_store import KeyringSecretStore, SecretStore

__all__ = [
    "CloudflareApiClient",
    "CloudflareApiConfig",
    "CloudflareApiTokenManager",
    "DeviceCodeResponse",
    "GitHubDeviceFlow",
    "GitHubOAuthConfig",
    "GitHubTokenManager",
    "HetznerApiKeyManager",
    "KeyringSecretStore",
    "SecretStore",
]
