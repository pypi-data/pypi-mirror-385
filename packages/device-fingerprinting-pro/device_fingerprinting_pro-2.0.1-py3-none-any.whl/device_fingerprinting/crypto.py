"""
Cryptographic primitives for device fingerprinting.
This module provides building blocks for encryption and key derivation.
"""

import os
import hmac
import hashlib
import json
import threading
from typing import Optional, Tuple, Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend

class ScryptKDF:
    """
    A wrapper for the Scrypt Key Derivation Function.
    """
    def __init__(self, salt_size: int = 16, n: int = 2**14, r: int = 8, p: int = 1, key_size: int = 32):
        self.salt_size = salt_size
        self.n = n
        self.r = r
        self.p = p
        self.key_size = key_size

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derives a key from the given password and salt.
        
        Args:
            password: The password to derive the key from.
            salt: The salt to use for the derivation.
            
        Returns:
            The derived key as bytes.
        """
        kdf = Scrypt(salt=salt, length=self.key_size, n=self.n, r=self.r, p=self.p)
        return kdf.derive(password.encode('utf-8'))

class AESGCMEncryptor:
    """
    Provides encryption and decryption using AES-GCM.
    """
    def __init__(self, key_size: int = 32, nonce_size: int = 12):
        if key_size not in [16, 24, 32]:
            raise ValueError("Invalid key size for AES. Must be 16, 24, or 32 bytes.")
        self.key_size = key_size
        self.nonce_size = nonce_size

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """
        Encrypts data using AES-GCM.
        
        Args:
            data: The data to encrypt.
            key: The encryption key.
            
        Returns:
            A blob containing nonce + ciphertext + tag.
        """
        if len(key) != self.key_size:
            raise ValueError(f"Key must be {self.key_size} bytes long.")
        
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.nonce_size)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt(self, encrypted_blob: bytes, key: bytes) -> bytes:
        """
        Decrypts an AES-GCM encrypted blob.
        
        Args:
            encrypted_blob: The blob to decrypt (nonce + ciphertext + tag).
            key: The decryption key.
            
        Returns:
            The original plaintext data.
            
        Raises:
            ValueError: If decryption fails due to wrong key or tampered data.
        """
        if len(key) != self.key_size:
            raise ValueError(f"Key must be {self.key_size} bytes long.")
            
        nonce = encrypted_blob[:self.nonce_size]
        ciphertext = encrypted_blob[self.nonce_size:]
        
        aesgcm = AESGCM(key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise ValueError("Decryption failed. The data may be tampered or the key is incorrect.")

class CryptoManager:
    """Handles cryptographic operations for device binding"""
    
    def __init__(self, password: bytes, salt: Optional[bytes] = None) -> None:
        self.backend = default_backend()
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password, self.salt)
        self.aesgcm = AESGCM(self.key)

    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        """Derive a 32-byte key for AES-256."""
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=self.backend
        )
        return kdf.derive(password)

    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Encrypts plaintext using AES-GCM."""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Decrypts ciphertext using AES-GCM."""
        nonce = ciphertext[:12]
        encrypted_data = ciphertext[12:]
        return self.aesgcm.decrypt(nonce, encrypted_data, associated_data)

    def sign(self, data: bytes) -> str:
        """Create HMAC-SHA-256 signature for data"""
        return hmac.new(self.key, data, hashlib.sha256).hexdigest()
    
    def verify(self, signature: str, data: bytes) -> bool:
        """Verify HMAC signature with constant-time comparison"""
        expected_sig = self.sign(data)
        return hmac.compare_digest(signature, expected_sig)

# Global instance management
_crypto_manager: Optional[CryptoManager] = None
_crypto_lock = threading.Lock()

def initialize_crypto_manager(password: str, salt: Optional[str] = None) -> None:
    """Initializes the global crypto manager with a password and optional salt."""
    global _crypto_manager
    with _crypto_lock:
        if _crypto_manager is None:
            password_bytes = password.encode('utf-8')
            salt_bytes = salt.encode('utf-8') if salt else None
            _crypto_manager = CryptoManager(password=password_bytes, salt=salt_bytes)

def get_crypto_manager() -> CryptoManager:
    """
    Get the global crypto manager.
    It must be initialized with initialize_crypto_manager first.
    """
    with _crypto_lock:
        if _crypto_manager is None:
            raise RuntimeError("CryptoManager has not been initialized. Call initialize_crypto_manager first.")
        return _crypto_manager

def sign_data(data: Dict[str, Any]) -> str:
    """Sign a data dictionary with HMAC"""
    payload = json.dumps(data, sort_keys=True).encode()
    return get_crypto_manager().sign(payload)

def verify_signature(signature: str, data: Dict[str, Any]) -> bool:
    """Verify HMAC signature of data dictionary"""
    payload = json.dumps(data, sort_keys=True).encode()
    return get_crypto_manager().verify(signature, payload)

def encrypt_data(plaintext: str, associated_data: Optional[str] = None) -> bytes:
    """Encrypts a string using the global crypto manager."""
    cm = get_crypto_manager()
    plaintext_bytes = plaintext.encode('utf-8')
    ad_bytes = associated_data.encode('utf-8') if associated_data else None
    return cm.encrypt(plaintext_bytes, ad_bytes)

def decrypt_data(ciphertext: bytes, associated_data: Optional[str] = None) -> str:
    """Decrypts a string using the global crypto manager."""
    cm = get_crypto_manager()
    ad_bytes = associated_data.encode('utf-8') if associated_data else None
    decrypted_bytes = cm.decrypt(ciphertext, ad_bytes)
    return decrypted_bytes.decode('utf-8')
