"""Configuration for Cloudflare API integration."""

from dataclasses import dataclass, field


@dataclass
class CloudflareApiConfig:
    """Configuration for Cloudflare API access.

    Cloudflare provides DNS management and other services via their REST API.
    This integration uses API tokens for authentication.
    """

    # Cloudflare API endpoints
    api_base_url: str = "https://api.cloudflare.com/client/v4"
    
    # DNS-specific endpoints
    zones_endpoint: str = "/zones"
    dns_records_endpoint: str = "/zones/{zone_id}/dns_records"
    
    # API token scopes (permissions) we request
    # For DNS management, typically includes: Zone:DNS:Edit and Zone:Zone:Read
    required_scopes: list[str] = field(default_factory=lambda: [
        "Zone:DNS:Edit",
        "Zone:Zone:Read",
    ])

    def __post_init__(self) -> None:
        """Initialize default scopes if not provided."""
        if self.required_scopes is None:
            self.required_scopes = [
                "Zone:DNS:Edit",
                "Zone:Zone:Read",
            ]

    @property
    def docs_url(self) -> str:
        """URL to Cloudflare API documentation."""
        return "https://developers.cloudflare.com/api/"

    @property
    def token_creation_url(self) -> str:
        """URL where users can create API tokens."""
        return "https://dash.cloudflare.com/profile/api-tokens"
