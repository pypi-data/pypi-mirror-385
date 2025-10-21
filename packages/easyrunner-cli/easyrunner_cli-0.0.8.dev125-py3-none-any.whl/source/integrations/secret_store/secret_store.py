"""Re-export SecretStore from core library for CLI compatibility.

This module re-exports the abstract SecretStore interface from the core library.
The concrete KeyringSecretStore implementation is in this CLI package.
"""

from easyrunner.source.store import SecretStore

__all__ = ["SecretStore"]
