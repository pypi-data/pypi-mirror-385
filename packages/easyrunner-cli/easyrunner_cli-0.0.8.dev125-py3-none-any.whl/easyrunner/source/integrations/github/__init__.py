"""GitHub integration module.

This module provides GitHub OAuth authentication and token management for
the core library. Can be used by CLI, Web API, and Web UI.
"""

from .github_device_flow import DeviceCodeResponse, GitHubDeviceFlow
from .github_oauth_config import GitHubOAuthConfig
from .github_token_manager import GitHubTokenManager

__all__ = [
    "DeviceCodeResponse",
    "GitHubDeviceFlow",
    "GitHubOAuthConfig",
    "GitHubTokenManager",
]
