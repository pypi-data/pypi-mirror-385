#!/usr/bin/env python3
"""
Fractal Group Ratchet - O(1) Group Encryption

Novel algorithm for efficient multi-party encryption.
"""

import secrets
import hashlib
import base64
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


class FractalGroupRatchet:
    """Fractal Group Ratchet - O(1) group encryption."""
    
    VERSION = "1.0.0"
    ALGORITHM = "fractal-group-ratchet-v1"
    LAYER_KEY_SALT = b"matp-fractal-layer-key-salt"
    SEED_ROTATION_SALT = b"matp-fractal-seed-rotation-salt"
    
    def __init__(self, group_seed: bytes = None):
        if group_seed is None:
            self.group_seed = secrets.token_bytes(32)
        elif isinstance(group_seed, bytes) and len(group_seed) == 32:
            self.group_seed = group_seed
        else:
            raise ValueError("Group seed must be 32 bytes")
        
        self.message_counter = 0
        self.seed_fingerprint = self._compute_fingerprint()
    
    def _compute_fingerprint(self) -> str:
        return hashlib.sha256(self.group_seed).hexdigest()[:16]
    
    def _derive_layer_key(self, layer_index: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.LAYER_KEY_SALT,
            info=f"fractal-layer-{layer_index}".encode('utf-8')
        ).derive(self.group_seed)
    
    def encrypt_for_group(self, plaintext: str) -> dict:
        layer_key = self._derive_layer_key(self.message_counter)
        cipher = AESGCM(layer_key)
        nonce = secrets.token_bytes(12)
        
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        ciphertext = cipher.encrypt(nonce, plaintext, None)
        
        envelope = {
            "version": self.VERSION,
            "algorithm": self.ALGORITHM,
            "layer": self.message_counter,
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "seed_fingerprint": self.seed_fingerprint,
            "timestamp": time.time()
        }
        
        self.message_counter += 1
        return envelope
    
    def decrypt_from_group(self, envelope: dict) -> str:
        if envelope.get("version") != self.VERSION:
            raise ValueError(f"Unsupported version: {envelope.get('version')}")
        if envelope.get("algorithm") != self.ALGORITHM:
            raise ValueError(f"Unsupported algorithm: {envelope.get('algorithm')}")
        if envelope["seed_fingerprint"] != self.seed_fingerprint:
            raise ValueError("Wrong group seed")
        
        layer_key = self._derive_layer_key(envelope["layer"])
        cipher = AESGCM(layer_key)
        nonce = base64.b64decode(envelope["nonce"])
        ciphertext = base64.b64decode(envelope["ciphertext"])
        
        plaintext = cipher.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    
    def export_session(self, from_layer: int = 0) -> dict:
        return {
            "version": self.VERSION,
            "algorithm": self.ALGORITHM,
            "group_seed": base64.b64encode(self.group_seed).decode('utf-8'),
            "start_layer": from_layer,
            "seed_fingerprint": self.seed_fingerprint,
            "exported_at": time.time()
        }
    
    def import_session(self, session_data: dict):
        if session_data.get("version") != self.VERSION:
            raise ValueError(f"Incompatible version")
        if session_data.get("algorithm") != self.ALGORITHM:
            raise ValueError(f"Incompatible algorithm")
        
        self.group_seed = base64.b64decode(session_data["group_seed"])
        self.message_counter = session_data["start_layer"]
        self.seed_fingerprint = self._compute_fingerprint()
        
        if self.seed_fingerprint != session_data["seed_fingerprint"]:
            raise ValueError("Session fingerprint mismatch")
    
    def rotate_seed(self) -> bytes:
        new_seed = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.SEED_ROTATION_SALT,
            info=b"seed-rotation"
        ).derive(self.group_seed)
        
        self.group_seed = new_seed
        self.message_counter = 0
        self.seed_fingerprint = self._compute_fingerprint()
        return new_seed
    
    def get_fingerprint(self) -> str:
        return self.seed_fingerprint
