"""Deprecated legacy module.

Historically this project stored settings and credentials in an encrypted file in the working directory.
The application now uses per-user storage (options.json under the user config directory) and stores
credentials via OS keyring with an encrypted-file fallback.

This module is kept only to avoid breaking old imports.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from config.encrypt_config import ConfigEncryptor


DECRYPTION_KEY = None


class ConfigDecryptor:
    def __init__(self, decryption_key=None):
        self.decryption_key = decryption_key

    def decrypt(self) -> Optional[Dict[str, Any]]:
        return ConfigEncryptor().load_config()

    def hello_world(self) -> str:
        return "Hello world"
