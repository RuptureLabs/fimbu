from __future__ import annotations

from typing import Any
import abc
import base64
import contextlib

from sqlalchemy import func as sql_func

cryptography = None
with contextlib.suppress(ImportError):
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes


class EncryptionBackend(abc.ABC):
    def mount_vault(self, key: str | bytes) -> None:
        if isinstance(key, str):
            key = key.encode()

    @abc.abstractmethod
    def init_engine(self, key: bytes | str) -> None:  # pragma: nocover
        pass

    @abc.abstractmethod
    def encrypt(self, value: Any) -> str:  # pragma: nocover
        pass

    @abc.abstractmethod
    def decrypt(self, value: Any) -> str:  # pragma: nocover
        pass


class PGCryptoBackend(EncryptionBackend):
    """PG Crypto backend."""

    def init_engine(self, key: bytes | str) -> None:
        if isinstance(key, str):
            key = key.encode()
        self.passphrase = base64.urlsafe_b64encode(key)

    def encrypt(self, value: Any) -> str:
        if not isinstance(value, str):  # pragma: nocover
            value = repr(value)
        value = value.encode()
        return sql_func.pgp_sym_encrypt(value, self.passphrase)  # type: ignore[return-value]

    def decrypt(self, value: Any) -> str:
        if not isinstance(value, str):  # pragma: nocover
            value = str(value)
        return sql_func.pgp_sym_decrypt(value, self.passphrase)  # type: ignore[return-value]


class FernetBackend(EncryptionBackend):
    """Encryption Using a Fernet backend"""

    def mount_vault(self, key: str | bytes) -> None:
        if isinstance(key, str):
            key = key.encode()
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(key)
        engine_key = digest.finalize()
        self.init_engine(engine_key)

    def init_engine(self, key: bytes | str) -> None:
        if isinstance(key, str):
            key = key.encode()
        self.key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(self.key)

    def encrypt(self, value: Any) -> str:
        if not isinstance(value, str):
            value = repr(value)
        value = value.encode()
        encrypted = self.fernet.encrypt(value)
        return encrypted.decode("utf-8")

    def decrypt(self, value: Any) -> str:
        if not isinstance(value, str):  # pragma: nocover
            value = str(value)
        decrypted: str | bytes = self.fernet.decrypt(value.encode())
        if not isinstance(decrypted, str):
            decrypted = decrypted.decode("utf-8")
        return decrypted
