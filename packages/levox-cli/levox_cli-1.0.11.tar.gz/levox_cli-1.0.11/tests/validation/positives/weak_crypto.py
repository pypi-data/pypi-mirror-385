#!/usr/bin/env python3
"""
Test file with weak cryptography issues.
Expected: Should detect weak crypto algorithms, hardcoded keys, and insecure practices.
"""

import hashlib
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def weak_hash_md5(data):
    """Using weak MD5 hash."""
    return hashlib.md5(data.encode()).hexdigest()

def weak_hash_sha1(data):
    """Using weak SHA1 hash."""
    return hashlib.sha1(data.encode()).hexdigest()

def weak_hash_sha256(data):
    """Using SHA256 (this is actually secure)."""
    return hashlib.sha256(data.encode()).hexdigest()

def weak_password_hash(password):
    """Weak password hashing without salt."""
    return hashlib.sha256(password.encode()).hexdigest()

def weak_password_hash_with_salt(password, salt):
    """Weak password hashing with insufficient iterations."""
    # Only 1000 iterations is too low
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000,  # Should be at least 100,000
    )
    return base64.b64encode(kdf.derive(password.encode()))

def hardcoded_encryption_key():
    """Hardcoded encryption key."""
    key = b"my_secret_key_12345"  # Hardcoded key
    return base64.b64encode(key)

def weak_random_generation():
    """Using weak random generation."""
    import random
    # Using random instead of secrets
    weak_random = random.randint(1, 1000)
    
    # Using os.urandom is actually secure
    secure_random = os.urandom(16)
    
    return weak_random, secure_random

def insecure_encryption():
    """Insecure encryption practices."""
    # Using base64 encoding as "encryption"
    def fake_encrypt(data):
        return base64.b64encode(data.encode()).decode()
    
    def fake_decrypt(encrypted_data):
        return base64.b64decode(encrypted_data.encode()).decode()
    
    # Using XOR with single byte key
    def xor_encrypt(data, key):
        return ''.join(chr(ord(c) ^ key) for c in data)
    
    return fake_encrypt, fake_decrypt, xor_encrypt

def weak_key_derivation():
    """Weak key derivation."""
    password = "weak_password"
    salt = b"static_salt"  # Static salt is bad
    
    # Insufficient iterations
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,  # Too short key length
        salt=salt,
        iterations=100,  # Way too few iterations
    )
    
    return kdf.derive(password.encode())

def insecure_storage():
    """Insecure storage of sensitive data."""
    # Storing password in plain text
    user_password = "user123"
    
    # Storing API key in plain text
    api_key = "sk_live_1234567890abcdef"
    
    # Storing private key in plain text
    private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
AgEAAoIBAQC7VJTUt9Us8cKB
-----END PRIVATE KEY-----"""
    
    return user_password, api_key, private_key

def weak_ssl_config():
    """Weak SSL/TLS configuration."""
    # Using weak cipher suites
    weak_ciphers = [
        "RC4",
        "DES",
        "3DES",
        "MD5"
    ]
    
    # Using weak protocols
    weak_protocols = [
        "SSLv2",
        "SSLv3",
        "TLSv1.0",
        "TLSv1.1"
    ]
    
    return weak_ciphers, weak_protocols
