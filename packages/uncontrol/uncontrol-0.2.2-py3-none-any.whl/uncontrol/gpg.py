"""
This module provides a wrapper class for GNU Privacy Guard (GPG) that adds additional functionality,
such as secure management of the GPG home directory and detailed error handling for encryption
and decryption.

Classes:
    - GPG: Extends `gnupg.GPG` with custom features to manage GPG keys and operations securely.

Modules Used:
    - logging: For logging debug or error information.
    - os: For interacting with the filesystem and managing file permissions.
    - shutil: For cleaning up temporary directories.
    - stat: For setting file and directory permissions.
    - tempfile: For creating secure temporary directories.
    - gnupg: For GPG operations.
"""

import logging
import os
import shutil
import stat
from tempfile import mkdtemp
from typing import Self, TYPE_CHECKING

from gnupg import GPG

from .exceptions import CryptoError

if TYPE_CHECKING:
    from .models import PrivateKey, PublicKey

logger = logging.getLogger(__name__)


class TemporaryGPG(GPG):
    """
    A custom wrapper for `gnupg.GPG` with enhanced key management, secure directory handling,
    and error management for encryption and decryption operations.

    Attributes:
        config (GPGConfig): Configuration object with GPG settings.
        gpg_home (str): Path to the temporary GPG home directory.
        _initialized (bool): Tracks whether the GPG environment has been initialized.
    """

    _initialized = False

    def __init__(self, private_keys: list["PrivateKey"], public_keys: list["PublicKey"]) -> None:
        """
        Initializes the GPG instance with a temporary GPG home
        and imports keys from the provided configuration.

        Args:
            config (GPGConfig): The configuration object containing key paths, passphrases,
            and settings.
        """
        self.private_keys = private_keys
        self.public_keys = public_keys
        self.gpg_home = mkdtemp()
        os.chmod(self.gpg_home, stat.S_IRWXU)  # Set permissions to 0700
        super().__init__(gnupghome=self.gpg_home, verbose=False)
        self.initialize_home()
        logger.debug("GPG is using %s as homedir", self.gpg_home)

    def __enter__(self) -> Self:
        """
        Context manager entry point. Initializes the GPG home directory.

        Returns:
            Self: The initialized GPG instance.
        """
        self.initialize_home()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit point. Cleans up the GPG home directory.
        """
        self.cleanup()

    def __del__(self):
        """Destructor to clean up the GPG home directory."""
        self.cleanup()

    def initialize_home(self) -> None:
        """
        Initializes the GPG home directory by importing public and private keys.
        """
        if self._initialized:
            return

        result = None
        for public_key in self.public_keys:
            result = self.import_keys(public_key.content)

        for private_key in self.private_keys:
            result = self.import_keys(private_key.content, passphrase=private_key.passphrase)

        if result is not None and result.returncode:
            raise CryptoError(f"Public key import failed: {result.stderr}")
        """
        with open(self.config.GPG_PUBLIC_KEY, "r", encoding="utf-8") as file:
            result = self.import_keys(file.read())
            if not result:
                raise CryptoError("Public key import failed")
        with open(self.config.GPG_SECRET_KEY, "r", encoding="utf-8") as file:
            result = self.import_keys(file.read())
            if not result:
                raise CryptoError("Private key import failed")
        """
        self.secure_gpg_home()
        self._initialized = True

    def secure_gpg_home(self) -> None:
        """
        Recursively sets permissions for all files and directories in the GPG home directory.
        Directories are set to 0700, and files are set to 0600.
        """
        for root, dirs, files in os.walk(self.gpg_home):
            # Set directories to 0700
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.chmod(dir_path, stat.S_IRWXU)
            # Set files to 0600
            for file_name in files:
                file_path = os.path.join(root, file_name)
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        logger.debug("Secured all contents of %s", self.gpg_home)

    def cleanup(self):
        """
        Deletes the temporary GPG home directory and resets the initialized flag.
        """
        shutil.rmtree(self.gpg_home, ignore_errors=True)
        self._initialized = False

    def get_decryption_kwargs(self, **kwargs) -> dict:
        """
        Constructs decryption keyword arguments using the configuration.

        Args:
            **kwargs: Additional keyword arguments to pass to the decryption method.

        Returns:
            dict: A dictionary of keyword arguments for decryption.
        """
        return {
            "always_trust": True,
            **kwargs,
        }

    def decrypt(self, message: str | bytes, **kwargs) -> str:
        """
        Decrypts a message using GPG.

        Args:
            message (str | bytes): The encrypted message to decrypt.
            **kwargs: Additional keyword arguments for decryption.

        Returns:
            str: The decrypted message as a string.

        Raises:
            CryptoError: If decryption fails and `GPG_IGNORE_ERRORS` is False.
        """
        kwargs = self.get_decryption_kwargs(**kwargs)
        # passphrase may differ
        # "passphrases": [key.passphrase for key in self.private_keys if key.passphrase],
        kwargs["passphrase"] = self.private_keys[0].passphrase
        gpg_crypt_obj = super().decrypt(message, **kwargs)
        if not gpg_crypt_obj.ok:
            err_msg = (
                f'GPG encryption error: status "{gpg_crypt_obj.status}" '
                f'(detail: "{gpg_crypt_obj.status_detail}")\n{str(message)}'
            )
            logger.error(err_msg)
            raise CryptoError(err_msg)
        return str(gpg_crypt_obj)

    def get_encryption_kwargs(self, **kwargs):
        """
        Constructs encryption keyword arguments using the configuration.

        Args:
            **kwargs: Additional keyword arguments to pass to the encryption method.

        Returns:
            dict: A dictionary of keyword arguments for encryption.
        """
        kwargs = {
            "always_trust": True,
            "armor": True,
            # "passphrase": self.config.GPG_PASSPHRASE,
            **kwargs,
        }
        return kwargs

    def encrypt(self, message: str | bytes, **kwargs) -> str:  # pylint: disable=arguments-differ
        """
        Encrypts a message using GPG.

        Args:
            message (str | bytes): The plaintext message to encrypt.
            **kwargs: Additional keyword arguments for encryption.

        Returns:
            str: The encrypted message.

        Raises:
            CryptoError: If encryption fails and `GPG_IGNORE_ERRORS` is False.
        """
        recipients = [key["keyid"] for key in self.list_keys()]
        kwargs = self.get_encryption_kwargs(**kwargs)
        gpg_crypt_obj = super().encrypt(message, recipients, **kwargs)
        if not gpg_crypt_obj.ok:
            logger.debug("%s", gpg_crypt_obj.stderr)  # pylint: disable=no-member
            err_msg = (
                f'GPG encryption error: status "{gpg_crypt_obj.status}" '
                f'(detail: "{gpg_crypt_obj.status_detail}")'
            )
            raise CryptoError(err_msg)
        logger.debug("Encryption successful")
        return str(gpg_crypt_obj)


def decrypt_symmetric(message: str, passphrase: str) -> str:
    decrypted_data = GPG().decrypt(
        message=message,
        passphrase=passphrase,
    )
    if not decrypted_data.ok:
        breakpoint()
        raise ValueError(f"Entschlüsselung fehlgeschlagen: {decrypted_data.status}")
    return str(decrypted_data)


def encrypt_symmetric(message: str, passphrase: str) -> str:
    encrypted_data = GPG().encrypt(
        data=message,
        recipients=None,
        symmetric='AES256',
        passphrase=passphrase,
        armor=True,
    )
    if not encrypted_data.ok:
        raise ValueError(f"Verschlüsselung fehlgeschlagen: {encrypted_data.status}")
    return str(encrypted_data)
