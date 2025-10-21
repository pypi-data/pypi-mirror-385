"""External service integrations for EasyRunner.

This module provides core business logic for integrating with external services
like GitHub, Cloudflare, and Hetzner. All integrations depend on abstract
interfaces (SecretStore, HttpClient) rather than concrete implementations,
allowing different interfaces (CLI, Web API, Web UI) to inject their own
implementations.
"""

from . import cloudflare, github, hetzner

__all__ = [
    "cloudflare",
    "github",
    "hetzner",
]
