# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/utils/services_auth.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

mcpgateway.utils.services_auth - Authentication utilities for MCP Gateway
Doctest examples
----------------
>>> import os
>>> from mcpgateway.utils import services_auth
>>> os.environ['AUTH_ENCRYPTION_SECRET'] = 'doctest-secret'
>>> services_auth.settings.auth_encryption_secret = 'doctest-secret'
>>> key = services_auth.get_key()
>>> isinstance(key, bytes)
True
>>> d = {'user': 'alice'}
>>> token = services_auth.encode_auth(d)
>>> isinstance(token, str)
True
>>> services_auth.decode_auth(token) == d
True
>>> services_auth.encode_auth(None) is None
True
>>> services_auth.decode_auth(None) == {}
True
>>> services_auth.settings.auth_encryption_secret = ''
>>> try:
...     services_auth.get_key()
... except ValueError as e:
...     print('error')
error
"""

# Standard
import base64
import hashlib
import json
import os

# Third-Party
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import SecretStr

# First-Party
from mcpgateway.config import settings


def get_key() -> bytes:
    """
    Generate a 32-byte AES encryption key derived from a passphrase.

    Returns:
        bytes: A 32-byte encryption key.

    Raises:
        ValueError: If the passphrase is not set or empty.

    Doctest:
    >>> import os
    >>> from mcpgateway.utils import services_auth
    >>> os.environ['AUTH_ENCRYPTION_SECRET'] = 'doctest-secret'
    >>> services_auth.settings.auth_encryption_secret = 'doctest-secret'
    >>> key = services_auth.get_key()
    >>> isinstance(key, bytes)
    True
    >>> services_auth.settings.auth_encryption_secret = ''
    >>> try:
    ...     services_auth.get_key()
    ... except ValueError as e:
    ...     print('error')
    error
    """
    passphrase = settings.auth_encryption_secret
    if not passphrase:
        raise ValueError("AUTH_ENCRYPTION_SECRET not set in environment.")

    # If it's SecretStr, extract the real value
    if isinstance(passphrase, SecretStr):
        passphrase = passphrase.get_secret_value()

    return hashlib.sha256(passphrase.encode()).digest()  # 32-byte key


def encode_auth(auth_value: dict) -> str:
    """
    Encrypt and encode an authentication dictionary into a compact base64-url string.

    Args:
        auth_value (dict): The authentication dictionary to encrypt and encode.

    Returns:
        str: A base64-url-safe encrypted string representing the dictionary, or None if input is None.

    Doctest:
    >>> import os
    >>> from mcpgateway.utils import services_auth
    >>> os.environ['AUTH_ENCRYPTION_SECRET'] = 'doctest-secret'
    >>> services_auth.settings.auth_encryption_secret = 'doctest-secret'
    >>> token = services_auth.encode_auth({'user': 'alice'})
    >>> isinstance(token, str)
    True
    >>> services_auth.encode_auth(None) is None
    True
    """
    if not auth_value:
        return None
    plaintext = json.dumps(auth_value)
    key = get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    combined = nonce + ciphertext
    encoded = base64.urlsafe_b64encode(combined).rstrip(b"=")
    return encoded.decode()


def decode_auth(encoded_value: str) -> dict:
    """
    Decode and decrypt a base64-url-safe encrypted string back into the authentication dictionary.

    Args:
        encoded_value (str): The encrypted base64-url string to decode and decrypt.

    Returns:
        dict: The decrypted authentication dictionary, or empty dict if input is None.

    Doctest:
    >>> import os
    >>> from mcpgateway.utils import services_auth
    >>> os.environ['AUTH_ENCRYPTION_SECRET'] = 'doctest-secret'
    >>> services_auth.settings.auth_encryption_secret = 'doctest-secret'
    >>> d = {'user': 'alice'}
    >>> token = services_auth.encode_auth(d)
    >>> services_auth.decode_auth(token) == d
    True
    >>> services_auth.decode_auth(None) == {}
    True
    """
    if not encoded_value:
        return {}
    key = get_key()
    aesgcm = AESGCM(key)
    # Fix base64 padding
    padded = encoded_value + "=" * (-len(encoded_value) % 4)
    combined = base64.urlsafe_b64decode(padded)
    nonce = combined[:12]
    ciphertext = combined[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())
