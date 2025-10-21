"""Keyring-based implementation of the SecretStore interface."""

import logging
import platform
from typing import Optional

import keyring

from easyrunner.source.store import SecretStore

logger = logging.getLogger(__name__)


class KeyringSecretStore(SecretStore):
    """Secure secret storage using the system keyring.

    Maps hierarchical path-based keys to keyring's service/account model:
    - Key path: "easyrunner/github/oauth_token"
    - Keyring service: "easyrunner.github"
    - Keyring account: "oauth_token"

    Uses the system keyring for secure credential storage. On macOS, this automatically
    configures keychain items to require password authentication on every access using
    the Security Framework. On other platforms, uses standard keyring storage.
    """

    def __init__(self) -> None:
        """Initialize the keyring secret store."""
        self.is_macos: bool = platform.system() == "Darwin"

    def store_secret(self, key: str, value: str) -> bool:
        """Store a secret in the system keyring."""
        service, account = self._parse_key(key)
        if self.is_macos:
            return self._store_secret_macos_secure(service, account, value)
        else:
            return self._store_secret_standard(service, account, value)

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret from the system keyring."""
        service, account = self._parse_key(key)
        if self.is_macos:
            return self._get_secret_macos_secure(service, account)
        else:
            return self._get_secret_standard(service, account)

    def delete_secret(self, key: str) -> bool:
        """Delete a secret from the system keyring."""
        service, account = self._parse_key(key)
        if self.is_macos:
            return self._delete_secret_macos_secure(service, account)
        else:
            return self._delete_secret_standard(service, account)

    @staticmethod
    def _parse_key(key: str) -> tuple[str, str]:
        """Parse path-based key into keyring service and account.

        Args:
            key: Path-based key (e.g., "easyrunner/github/oauth_token")

        Returns:
            Tuple of (service, account) for keyring
        """
        parts = key.split("/")

        if len(parts) < 2:
            raise ValueError(f"Invalid key format: {key}. Expected format: easyrunner/service/...")

        # Convert "easyrunner/github/oauth_token" to service="easyrunner.github", account="oauth_token"
        service = f"{parts[0]}.{parts[1]}"
        account = "/".join(parts[2:]) if len(parts) > 2 else ""

        return service, account

    def _store_secret_standard(self, service: str, account: str, value: str) -> bool:
        """Store secret using standard keyring (non-macOS platforms)."""
        try:
            keyring.set_password(service, account, value)
            logger.debug(f"Secret stored in keyring: {service}/{account}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret in keyring: {e}")
            return False

    def _get_secret_standard(self, service: str, account: str) -> Optional[str]:
        """Retrieve secret using standard keyring (non-macOS platforms)."""
        try:
            secret = keyring.get_password(service, account)
            if secret:
                logger.debug(f"Secret retrieved from keyring: {service}/{account}")
            return secret
        except Exception as e:
            logger.error(f"Failed to retrieve secret from keyring: {e}")
            return None

    def _delete_secret_standard(self, service: str, account: str) -> bool:
        """Delete secret using standard keyring (non-macOS platforms)."""
        try:
            keyring.delete_password(service, account)
            logger.debug(f"Secret deleted from keyring: {service}/{account}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret from keyring: {e}")
            return False

    def _store_secret_macos_secure(
        self, service: str, account: str, value: str
    ) -> bool:
        """Store secret with password challenge requirement on macOS."""
        try:
            from Foundation import NSData  # type: ignore
            from Security import (  # type: ignore
                SecAccessControlCreateWithFlags,  # type: ignore
                SecItemAdd,  # type: ignore
                SecItemDelete,  # type: ignore
                errSecSuccess,  # type: ignore
                kSecAttrAccessControl,  # type: ignore
                kSecAttrAccessibleWhenUnlockedThisDeviceOnly,  # type: ignore
                kSecAttrAccount,  # type: ignore
                kSecAttrService,  # type: ignore
                kSecClass,  # type: ignore
                kSecClassGenericPassword,  # type: ignore
                kSecValueData,  # type: ignore
            )
        except ImportError as import_error:
            logger.info(
                f"PyObjC frameworks not available ({import_error}), using standard keyring"
            )
            return self._store_secret_standard(service, account, value)

        try:
            # Delete any existing item first
            query = {
                kSecClass: kSecClassGenericPassword,
                kSecAttrService: service,
                kSecAttrAccount: account,
            }
            SecItemDelete(query)

            # Create access control requiring user interaction (password/TouchID)
            # Using kSecAccessControlUserPresence which requires authentication
            error = None
            access_control = SecAccessControlCreateWithFlags(
                None,  # allocator
                kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
                0x40000000,  # kSecAccessControlUserPresence
                error,
            )

            if not access_control:
                logger.warning(
                    "Failed to create access control, falling back to standard keyring"
                )
                return self._store_secret_standard(service, account, value)

            # Configure keychain item with password requirement
            value_bytes = value.encode("utf-8")
            query = {
                kSecClass: kSecClassGenericPassword,
                kSecAttrService: service,
                kSecAttrAccount: account,
                kSecValueData: NSData.dataWithBytes_length_(value_bytes, len(value_bytes)),
                kSecAttrAccessControl: access_control,
            }

            status = SecItemAdd(query, None)
            if status == errSecSuccess:
                logger.debug(
                    f"Secret stored with password challenge requirement: {service}/{account}"
                )
                return True
            else:
                logger.warning(
                    f"Failed to store secret (status: {status}), falling back to standard keyring"
                )
                return self._store_secret_standard(service, account, value)

        except Exception as e:
            logger.warning(
                f"Failed to store secret securely: {e}, falling back to standard keyring"
            )
            return self._store_secret_standard(service, account, value)

    def _get_secret_macos_secure(self, service: str, account: str) -> Optional[str]:
        """Retrieve secret with password challenge on macOS."""
        try:
            from Security import (  # type: ignore
                SecItemCopyMatching,  # type: ignore
                errSecAuthFailed,  # type: ignore
                errSecItemNotFound,  # type: ignore
                errSecSuccess,  # type: ignore
                kSecAttrAccount,  # type: ignore
                kSecAttrService,  # type: ignore
                kSecClass,  # type: ignore
                kSecClassGenericPassword,  # type: ignore
                kSecReturnData,  # type: ignore
            )
        except ImportError as import_error:
            logger.info(
                f"PyObjC frameworks not available ({import_error}), using standard keyring"
            )
            return self._get_secret_standard(service, account)

        try:
            query = {
                kSecClass: kSecClassGenericPassword,
                kSecAttrService: service,
                kSecAttrAccount: account,
                kSecReturnData: True,
            }

            result = None
            status = SecItemCopyMatching(query, result)

            if status == errSecSuccess and result:
                value = result[0].bytes().tobytes().decode("utf-8")
                logger.debug(f"Secret retrieved from keyring: {service}/{account}")
                return value
            elif status == errSecItemNotFound:
                logger.debug(f"Secret not found in keyring: {service}/{account}")
                return None
            elif status == errSecAuthFailed:
                logger.error("Authentication failed when retrieving secret")
                return None
            else:
                logger.warning(
                    f"Failed to retrieve secret (status: {status}), falling back to standard keyring"
                )
                return self._get_secret_standard(service, account)

        except Exception as e:
            logger.warning(
                f"Failed to retrieve secret securely: {e}, falling back to standard keyring"
            )
            return self._get_secret_standard(service, account)

    def _delete_secret_macos_secure(self, service: str, account: str) -> bool:
        """Delete secret on macOS."""
        try:
            from Security import (  # type: ignore
                SecItemDelete,  # type: ignore
                errSecSuccess,  # type: ignore
                kSecAttrAccount,  # type: ignore
                kSecAttrService,  # type: ignore
                kSecClass,  # type: ignore
                kSecClassGenericPassword,  # type: ignore
            )
        except ImportError as import_error:
            logger.info(
                f"PyObjC frameworks not available ({import_error}), using standard keyring"
            )
            return self._delete_secret_standard(service, account)

        try:
            query = {
                kSecClass: kSecClassGenericPassword,
                kSecAttrService: service,
                kSecAttrAccount: account,
            }

            status = SecItemDelete(query)
            if status == errSecSuccess:
                logger.debug(f"Secret deleted from keyring: {service}/{account}")
                return True
            else:
                logger.warning(
                    f"Failed to delete secret (status: {status}), falling back to standard keyring"
                )
                return self._delete_secret_standard(service, account)

        except Exception as e:
            logger.warning(
                f"Failed to delete secret securely: {e}, falling back to standard keyring"
            )
            return self._delete_secret_standard(service, account)
