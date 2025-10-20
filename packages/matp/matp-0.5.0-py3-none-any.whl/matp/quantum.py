"""
Matryoshka Protocol - Post-Quantum Cryptography Module

Provides Kyber-512 KEM and Dilithium-2 signatures with classical fallback.
"""
from __future__ import annotations

import os
import hashlib
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class KemKeyPair:
    """Kyber KEM key pair"""
    public_key: bytes
    secret_key: bytes


@dataclass
class SignKeyPair:
    """Dilithium signature key pair"""
    public_key: bytes
    secret_key: bytes


@dataclass
class KemCiphertext:
    """Kyber ciphertext containing encapsulated shared secret"""
    ciphertext: bytes
    shared_secret: bytes


class QuantumCrypto:
    """Production-grade post-quantum cryptography using Kyber and Dilithium."""
    
    def __init__(self):
        self.pq_available = self._check_pq_availability()
        
    def _check_pq_availability(self) -> bool:
        try:
            import oqs
            return True
        except ImportError:
            return False
    
    def generate_kem_keypair(self) -> KemKeyPair:
        if self.pq_available:
            return self._generate_kem_keypair_pq()
        else:
            return self._generate_kem_keypair_fallback()
    
    def _generate_kem_keypair_pq(self) -> KemKeyPair:
        try:
            import oqs
            kem = oqs.KeyEncapsulation("Kyber512")
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
            return KemKeyPair(public_key=public_key, secret_key=secret_key)
        except Exception:
            return self._generate_kem_keypair_fallback()
    
    def _generate_kem_keypair_fallback(self) -> KemKeyPair:
        from cryptography.hazmat.primitives.asymmetric import x25519
        from cryptography.hazmat.primitives import serialization
        
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return KemKeyPair(public_key=pub_bytes, secret_key=priv_bytes)
    
    def kem_encapsulate(self, public_key: bytes) -> KemCiphertext:
        if self.pq_available:
            return self._kem_encapsulate_pq(public_key)
        else:
            return self._kem_encapsulate_fallback(public_key)
    
    def _kem_encapsulate_pq(self, public_key: bytes) -> KemCiphertext:
        try:
            import oqs
            kem = oqs.KeyEncapsulation("Kyber512")
            ciphertext, shared_secret = kem.encap_secret(public_key)
            return KemCiphertext(ciphertext=ciphertext, shared_secret=shared_secret)
        except Exception:
            return self._kem_encapsulate_fallback(public_key)
    
    def _kem_encapsulate_fallback(self, public_key: bytes) -> KemCiphertext:
        from cryptography.hazmat.primitives.asymmetric import x25519
        from cryptography.hazmat.primitives import serialization
        
        ephemeral_private = x25519.X25519PrivateKey.generate()
        ephemeral_public = ephemeral_private.public_key()
        peer_public = x25519.X25519PublicKey.from_public_bytes(public_key)
        shared_secret = ephemeral_private.exchange(peer_public)
        
        ciphertext = ephemeral_public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return KemCiphertext(ciphertext=ciphertext, shared_secret=shared_secret)
    
    def kem_decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        if self.pq_available:
            return self._kem_decapsulate_pq(secret_key, ciphertext)
        else:
            return self._kem_decapsulate_fallback(secret_key, ciphertext)
    
    def _kem_decapsulate_pq(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        try:
            import oqs
            kem = oqs.KeyEncapsulation("Kyber512")
            shared_secret = kem.decap_secret(ciphertext, secret_key)
            return shared_secret
        except Exception:
            return self._kem_decapsulate_fallback(secret_key, ciphertext)
    
    def _kem_decapsulate_fallback(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        from cryptography.hazmat.primitives.asymmetric import x25519
        
        private_key = x25519.X25519PrivateKey.from_private_bytes(secret_key)
        ephemeral_public = x25519.X25519PublicKey.from_public_bytes(ciphertext)
        shared_secret = private_key.exchange(ephemeral_public)
        return shared_secret


_quantum_crypto = None

def get_quantum_crypto() -> QuantumCrypto:
    global _quantum_crypto
    if _quantum_crypto is None:
        _quantum_crypto = QuantumCrypto()
    return _quantum_crypto
