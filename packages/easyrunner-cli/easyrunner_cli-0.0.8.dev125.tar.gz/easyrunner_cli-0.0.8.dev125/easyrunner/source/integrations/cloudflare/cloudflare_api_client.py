"""Cloudflare API client for managing DNS records and zones.

This module provides core business logic for interacting with Cloudflare API.
Depends on HttpClient for HTTP operations, allowing different interfaces to
provide custom implementations if needed.
"""

import logging
from typing import Any, Optional

from ...http_client import HttpClient
from .cloudflare_api_config import CloudflareApiConfig

logger = logging.getLogger(__name__)


class CloudflareApiClient:
    """Client for interacting with Cloudflare API.

    Handles authentication and provides methods for common DNS operations:
    - List zones
    - Get zone details
    - List DNS records
    - Create DNS records
    - Update DNS records
    - Delete DNS records

    Args:
        api_token: Cloudflare API token for authentication
        config: Optional CloudflareApiConfig. Uses defaults if not provided.
        http_client: Optional HttpClient instance. Creates default if not provided.
    """

    def __init__(
        self, 
        api_token: str, 
        config: Optional[CloudflareApiConfig] = None,
        http_client: Optional[HttpClient] = None
    ) -> None:
        """Initialize Cloudflare API client.

        Args:
            api_token: Cloudflare API token for authentication
            config: Optional CloudflareApiConfig. Uses defaults if not provided.
            http_client: Optional HttpClient instance. Creates default if not provided.

        Raises:
            ValueError: If api_token is empty or None
        """
        if not api_token or not api_token.strip():
            raise ValueError("API token cannot be empty")

        self.api_token = api_token
        self.config = config or CloudflareApiConfig()
        
        if http_client is not None:
            self.http_client = http_client
        else:
            self.http_client = HttpClient(
                base_url=self.config.api_base_url,
                auth_token=api_token,
                auth_type="Bearer"
            )

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for Cloudflare API requests.

        Returns:
            Dictionary of headers including Content-Type
        """
        return {
            "Content-Type": "application/json",
        }

    def test_token(self) -> bool:
        """Test if the API token is valid.

        Makes a simple API call to verify token validity.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = self.http_client.get(
                endpoint="/user/tokens/verify",
                headers=self._get_headers(),
            )
            return response.success
        except Exception as e:
            logger.debug(f"Token verification failed: {e}")
            return False

    def list_zones(self) -> Optional[list[dict[str, Any]]]:
        """List all zones for the account.

        Returns:
            List of zone dictionaries with 'id', 'name', 'status', etc., or None on error
        """
        try:
            response = self.http_client.get(
                endpoint=self.config.zones_endpoint,
                headers=self._get_headers(),
            )
            if response.success and isinstance(response.data, dict):
                return response.data.get("result", [])
            else:
                logger.error(f"Failed to list zones: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error listing zones: {e}")
            return None

    def get_zone(self, zone_name: str) -> Optional[dict[str, Any]]:
        """Get zone details by name.

        Args:
            zone_name: Domain name of the zone (e.g., "example.com")

        Returns:
            Zone dictionary with id, name, status, etc., or None if not found
        """
        try:
            zones = self.list_zones()
            if not zones:
                return None

            for zone in zones:
                if zone.get("name") == zone_name:
                    return zone

            logger.warning(f"Zone '{zone_name}' not found")
            return None
        except Exception as e:
            logger.error(f"Error getting zone '{zone_name}': {e}")
            return None

    def list_dns_records(self, zone_id: str) -> Optional[list[dict[str, Any]]]:
        """List all DNS records for a zone.

        Args:
            zone_id: Cloudflare zone ID

        Returns:
            List of DNS record dictionaries or None on error
        """
        try:
            endpoint = self.config.dns_records_endpoint.format(zone_id=zone_id)
            response = self.http_client.get(
                endpoint=endpoint,
                headers=self._get_headers(),
            )
            if response.success and isinstance(response.data, dict):
                return response.data.get("result", [])
            else:
                logger.error(f"Failed to list DNS records: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error listing DNS records for zone {zone_id}: {e}")
            return None

    def create_dns_record(
        self,
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = False,
    ) -> Optional[dict[str, Any]]:
        """Create a new DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_type: DNS record type (A, AAAA, CNAME, MX, TXT, etc.)
            name: Record name/hostname
            content: Record value
            ttl: Time to live in seconds (1 = auto, min 60 for non-proxied)
            proxied: Whether to proxy through Cloudflare

        Returns:
            Created DNS record dictionary or None on error
        """
        try:
            endpoint = self.config.dns_records_endpoint.format(zone_id=zone_id)
            data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied,
            }

            response = self.http_client.post(
                endpoint=endpoint,
                headers=self._get_headers(),
                json_data=data,
            )

            if response.success and isinstance(response.data, dict):
                return response.data.get("result")
            else:
                logger.error(f"Failed to create DNS record: {response.status_code}")
                if isinstance(response.data, dict):
                    errors = response.data.get("errors", [])
                    logger.error(f"API errors: {errors}")
                return None
        except Exception as e:
            logger.error(f"Error creating DNS record: {e}")
            return None

    def update_dns_record(
        self,
        zone_id: str,
        record_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = False,
    ) -> Optional[dict[str, Any]]:
        """Update an existing DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_id: Cloudflare DNS record ID
            record_type: DNS record type
            name: Record name/hostname
            content: Record value
            ttl: Time to live in seconds
            proxied: Whether to proxy through Cloudflare

        Returns:
            Updated DNS record dictionary or None on error
        """
        try:
            endpoint = self.config.dns_records_endpoint.format(zone_id=zone_id)
            data = {
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied,
            }

            response = self.http_client.put(
                endpoint=f"{endpoint}/{record_id}",
                headers=self._get_headers(),
                json_data=data,
            )

            if response.success and isinstance(response.data, dict):
                return response.data.get("result")
            else:
                logger.error(f"Failed to update DNS record: {response.status_code}")
                if isinstance(response.data, dict):
                    errors = response.data.get("errors", [])
                    logger.error(f"API errors: {errors}")
                return None
        except Exception as e:
            logger.error(f"Error updating DNS record: {e}")
            return None

    def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """Delete a DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_id: Cloudflare DNS record ID

        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            endpoint = self.config.dns_records_endpoint.format(zone_id=zone_id)
            response = self.http_client.delete(
                endpoint=f"{endpoint}/{record_id}",
                headers=self._get_headers(),
            )

            if response.success:
                return True
            else:
                logger.error(f"Failed to delete DNS record: {response.status_code}")
                if isinstance(response.data, dict):
                    errors = response.data.get("errors", [])
                    logger.error(f"API errors: {errors}")
                return False
        except Exception as e:
            logger.error(f"Error deleting DNS record: {e}")
            return False
