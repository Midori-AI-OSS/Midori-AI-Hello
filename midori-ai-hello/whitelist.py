"""Whitelist profile storage with model-based encryption.

This module provides the :class:`WhitelistManager` class for managing a list
of authorised user profiles. Profiles are stored in
``~/.midoriai/whitelist.json`` and encrypted using a key derived from
``sha512`` of the trained model weights combined with a machine-specific
secret. The key derivation follows the approach documented in
``.codex/implementation/profile-encryption.md``.

The encryption scheme uses :class:`cryptography.fernet.Fernet`. A companion
``whitelist.hash`` file stores the model hash used for encryption so that the
application can detect when the active model has changed.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import uuid
from pathlib import Path
from typing import List

from cryptography.fernet import Fernet


log = logging.getLogger(__name__)


class WhitelistManager:
    """Manage encrypted whitelist profiles."""

    def __init__(self, model_path: Path, config_dir: Path | None = None) -> None:
        self.model_path = Path(model_path)
        self.config_dir = config_dir or Path.home() / ".midoriai"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.whitelist_file = self.config_dir / "whitelist.json"
        self.hash_file = self.config_dir / "whitelist.hash"
        self.uuid_file = self.config_dir / "hellouuid.txt"
        log.debug("WhitelistManager initialised at %s", self.config_dir)

    # ------------------------------------------------------------------
    # Key handling
    # ------------------------------------------------------------------
    def _model_hash(self) -> str:
        data = self.model_path.read_bytes()
        return hashlib.sha512(data).hexdigest()

    def _host_hash(self) -> str:
        if self.uuid_file.exists():
            lines = [line.strip() for line in self.uuid_file.read_text().splitlines() if line.strip()]
            valid = len(lines) == 2
            if valid:
                try:
                    for line in lines:
                        uuid.UUID(line)
                except ValueError:
                    valid = False
            if not valid:
                self.uuid_file.write_text(f"{uuid.uuid4()}\n{uuid.uuid4()}\n")
        else:
            self.uuid_file.write_text(f"{uuid.uuid4()}\n{uuid.uuid4()}\n")
        secret = self.uuid_file.read_text()
        return hashlib.sha512(secret.encode()).hexdigest()

    def _derive_key(self, model_hash: str, host_hash: str) -> bytes:
        combined_int = (int(model_hash, 16) + int(host_hash, 16)) % (1 << 512)
        combined_bytes = combined_int.to_bytes(64, "big")
        return base64.urlsafe_b64encode(combined_bytes[:32])

    def _fernet(self) -> Fernet:
        return Fernet(self._derive_key(self._model_hash(), self._host_hash()))

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _write(self, profiles: List[str]) -> None:
        token = self._fernet().encrypt(json.dumps(profiles).encode("utf-8"))
        self.whitelist_file.write_bytes(token)
        self.hash_file.write_text(self._model_hash())

    def _read(self) -> List[str]:
        if not self.whitelist_file.exists():
            return []
        token = self.whitelist_file.read_bytes()
        current_hash = self._model_hash()
        stored_hash = (
            self.hash_file.read_text().strip()
            if self.hash_file.exists()
            else current_hash
        )
        if stored_hash == current_hash:
            fernet = self._fernet()
        else:
            fernet = Fernet(self._derive_key(stored_hash, self._host_hash()))
        data = fernet.decrypt(token)
        return json.loads(data.decode("utf-8"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_user(self, name: str) -> None:
        profiles = self._read()
        if name not in profiles:
            profiles.append(name)
            self._write(profiles)
            log.info("Added user %s to whitelist", name)

    def remove_user(self, name: str) -> None:
        profiles = self._read()
        if name in profiles:
            profiles.remove(name)
            self._write(profiles)
            log.info("Removed user %s from whitelist", name)

    def users(self) -> List[str]:
        return self._read()

    # ------------------------------------------------------------------
    # Key rotation / model change
    # ------------------------------------------------------------------
    def is_hash_mismatch(self) -> bool:
        if not self.hash_file.exists():
            return False
        stored = self.hash_file.read_text().strip()
        return stored != self._model_hash()

    def reencrypt(self) -> None:
        """Re-encrypt the whitelist using the current model hash.

        The existing whitelist is decrypted using the hash recorded in
        ``whitelist.hash`` so that a model update does not lose stored
        profiles.
        """

        if not self.whitelist_file.exists():
            return

        stored_hash = self.hash_file.read_text().strip() if self.hash_file.exists() else None
        token = self.whitelist_file.read_bytes()
        if stored_hash:
            old_fernet = Fernet(self._derive_key(stored_hash, self._host_hash()))
        else:
            old_fernet = self._fernet()
        data = old_fernet.decrypt(token)
        profiles = json.loads(data.decode("utf-8"))
        self._write(profiles)
