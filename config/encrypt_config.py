from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import platformdirs
import keyring
from cryptography.fernet import Fernet


APP_NAME = "Image Processor"
APP_AUTHOR = "images_py"
KEYRING_SERVICE = "images_py.image_processor"

PERSISTED_OPTION_KEYS = {
    "canvas_width",
    "canvas_height",
    "template",
    "delete_images",
    "transparent",
    "background_color",
    "image_format",
    "image_size",
    "destination_path",
    "selected_directory",
}

# Legacy key used ONLY to decrypt an existing legacy ./config.enc and migrate it.
LEGACY_FERNET_KEY = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="


def _config_dir() -> Path:
    path = Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _options_path() -> Path:
    return _config_dir() / "options.json"


def _secrets_enc_path() -> Path:
    # Only used if keyring is unavailable.
    return _config_dir() / "credentials.enc"


def _master_key_path() -> Path:
    # Only used if keyring is unavailable.
    return _config_dir() / "master.key"


def _legacy_candidates() -> List[Path]:
    candidates: List[Path] = []
    try:
        candidates.append(Path.cwd() / "config.enc")
    except Exception:
        pass

    try:
        candidates.append(Path(sys.argv[0]).resolve().parent / "config.enc")
    except Exception:
        pass

    # Deduplicate while keeping order
    seen = set()
    unique: List[Path] = []
    for c in candidates:
        if str(c) not in seen:
            seen.add(str(c))
            unique.append(c)
    return unique


def _try_keyring_get(username: str) -> Optional[str]:
    try:
        return keyring.get_password(KEYRING_SERVICE, username)
    except Exception:
        return None


def _try_keyring_set(username: str, value: str) -> bool:
    try:
        keyring.set_password(KEYRING_SERVICE, username, value)
        return True
    except Exception:
        return False


def _get_or_create_master_key() -> bytes:
    # 1) Allow overriding in dev/CI
    env_key = os.environ.get("IMAGE_PROCESSOR_MASTER_KEY")
    if env_key:
        try:
            return env_key.encode() if isinstance(env_key, str) else env_key
        except Exception:
            pass

    # 2) Prefer OS keyring
    stored = _try_keyring_get("master_key")
    if stored:
        return stored.encode()

    # 3) Fallback to per-user file
    key_path = _master_key_path()
    if key_path.exists():
        try:
            return key_path.read_bytes().strip()
        except Exception:
            pass

    new_key = Fernet.generate_key()
    if not _try_keyring_set("master_key", new_key.decode()):
        # best-effort file persistence
        try:
            key_path.write_bytes(new_key)
        except Exception:
            pass
    return new_key


def _load_options() -> Dict[str, Any]:
    path = _options_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        cleaned = {k: v for k, v in data.items() if k in PERSISTED_OPTION_KEYS}
        # If we had to drop keys, persist the cleaned version.
        if cleaned != data:
            try:
                _save_options(cleaned)
            except Exception:
                pass
        return cleaned
    except Exception:
        return {}


def _save_options(options: Dict[str, Any]) -> None:
    path = _options_path()
    path.write_text(json.dumps(options, indent=2), encoding="utf-8")


def _load_credentials_list() -> List[Dict[str, Any]]:
    # Prefer keyring storage
    raw = _try_keyring_get("credentials_json")
    if raw:
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    # Fallback: encrypted file in per-user config dir
    enc_path = _secrets_enc_path()
    if enc_path.exists():
        try:
            f = Fernet(_get_or_create_master_key())
            decrypted = f.decrypt(enc_path.read_bytes()).decode("utf-8")
            data = json.loads(decrypted)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    return []


def _save_credentials_list(credentials_list: List[Dict[str, Any]]) -> None:
    payload = json.dumps(credentials_list)

    # Prefer keyring
    if _try_keyring_set("credentials_json", payload):
        return

    # Fallback: encrypted file
    f = Fernet(_get_or_create_master_key())
    enc = f.encrypt(payload.encode("utf-8"))
    _secrets_enc_path().write_bytes(enc)


def _migrate_legacy_config_if_present() -> None:
    # One-time migration from legacy ./config.enc using LEGACY_FERNET_KEY.
    for legacy_path in _legacy_candidates():
        if not legacy_path.exists():
            continue
        try:
            encrypted_data = legacy_path.read_bytes()
            decrypted_data = Fernet(LEGACY_FERNET_KEY).decrypt(encrypted_data).decode("utf-8")
            legacy_config = json.loads(decrypted_data)
        except Exception:
            continue

        legacy_options = legacy_config.get("options") if isinstance(legacy_config, dict) else None
        if isinstance(legacy_options, dict):
            _save_options(legacy_options)

        legacy_credentials = legacy_config.get("credentials") if isinstance(legacy_config, dict) else None
        credentials_list: List[Dict[str, Any]] = []
        if isinstance(legacy_credentials, list):
            credentials_list = [c for c in legacy_credentials if isinstance(c, dict)]
        elif isinstance(legacy_credentials, dict):
            legacy_credentials["active"] = True
            credentials_list = [legacy_credentials]

        if credentials_list:
            # Ensure only one is active
            active_found = False
            for c in credentials_list:
                if c.get("active") and not active_found:
                    active_found = True
                elif c.get("active") and active_found:
                    c["active"] = False
            if not active_found:
                credentials_list[0]["active"] = True

            _get_or_create_master_key()  # generate new key (v2) for per-user storage
            _save_credentials_list(credentials_list)

        # Remove legacy file after successful migration
        try:
            legacy_path.unlink(missing_ok=True)
        except Exception:
            pass


class ConfigEncryptor:
    """Compatibility wrapper.

    Historically this class wrote `config.enc` in the working directory with a hardcoded key.
    It now stores per-user config (options.json) and secrets (keyring or encrypted fallback).
    """

    def __init__(self, key: Optional[bytes] = None, filename: str = "config.enc"):
        self.key = key  # kept for backward compatibility; no longer required
        self.filename = filename  # kept for backward compatibility

        # One-time legacy migration
        _migrate_legacy_config_if_present()

        # Ensure a v2 key exists (for encrypted-file fallback)
        _get_or_create_master_key()

    def get_key(self) -> str:
        # Return the v2 master key (mainly useful for debugging).
        return _get_or_create_master_key().decode("utf-8")

    def save_credentials(self, credentials: Dict[str, Any]) -> None:
        config = self.load_config() or {"credentials": [], "options": {}}
        credentials_list = config.get("credentials", [])
        if not isinstance(credentials_list, list):
            credentials_list = []

        # Update existing or append
        existing = None
        for cred in credentials_list:
            if isinstance(cred, dict) and cred.get("nice_name") == credentials.get("nice_name"):
                existing = cred
                break

        if existing is not None:
            existing.update(credentials)
        else:
            credentials_list.append(credentials)

        # Mark active
        target = credentials.get("nice_name")
        for cred in credentials_list:
            if isinstance(cred, dict):
                cred["active"] = cred.get("nice_name") == target

        _save_credentials_list([c for c in credentials_list if isinstance(c, dict)])

    def delete_credentials(self, credentials: str) -> None:
        config = self.load_config() or {"credentials": [], "options": {}}
        credentials_list = config.get("credentials", [])
        if not isinstance(credentials_list, list):
            credentials_list = []

        remaining = [c for c in credentials_list if isinstance(c, dict) and c.get("nice_name") != credentials]
        if remaining:
            # Ensure one active remains
            if not any(c.get("active") for c in remaining):
                remaining[0]["active"] = True
        _save_credentials_list(remaining)

    def save_options(self, options: Dict[str, Any]) -> None:
        serializable_options = {
            k: v
            for k, v in options.items()
            if k in PERSISTED_OPTION_KEYS and self.is_json_serializable(v)
        }
        _save_options(serializable_options)

    def load_config(self) -> Optional[Dict[str, Any]]:
        return {
            "credentials": _load_credentials_list(),
            "options": _load_options(),
        }

    def load_credentials(self) -> Optional[Dict[str, Any]]:
        config = self.load_config()
        if not config:
            return None
        credentials_list = config.get("credentials", [])
        if isinstance(credentials_list, list):
            for credentials in credentials_list:
                if isinstance(credentials, dict) and credentials.get("active"):
                    return credentials
            return credentials_list[0] if credentials_list else None
        if isinstance(credentials_list, dict):
            return credentials_list
        return None

    @staticmethod
    def is_json_serializable(value: Any) -> bool:
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False
