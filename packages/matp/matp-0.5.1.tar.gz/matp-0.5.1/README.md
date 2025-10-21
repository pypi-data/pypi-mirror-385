# Matryoshka Protocol (MATP)

Invisible secure messaging with steganography, post-quantum cryptography, and zero-knowledge proofs.

## 📦 Features

- **Invisible messaging** - Hide encrypted messages in normal web traffic
- **Post-quantum cryptography** - Kyber-512 KEM and Dilithium-2 signatures
- **Group messaging** - Fractal Group Ratchet for efficient group encryption
- **Zero-knowledge proofs** - Sigma protocol for plausible deniability
- **Multiple steganography modes** - JSON API, EXIF, Fast Ghost
- **Classical crypto fallback** - X25519, Ed25519, AES-256-GCM

## 📦 Installation

```bash
pip install matp
```

## 🚀 Quick Start

### 1. Basic 1-to-1 Messaging

```python
from matp import MatryoshkaProtocol

# Initialize
alice = MatryoshkaProtocol()
bob = MatryoshkaProtocol()

# Key exchange (X25519)
alice_priv, alice_pub = MatryoshkaProtocol.generate_keypair()
bob_priv, bob_pub = MatryoshkaProtocol.generate_keypair()

shared_secret = MatryoshkaProtocol.derive_shared_secret(alice_priv, bob_pub)
alice_session = MatryoshkaProtocol(key=shared_secret)
bob_session = MatryoshkaProtocol(key=shared_secret)

# Send invisible message
msg = alice_session.send_message("Secret meeting at midnight")
# Looks like: {"status": "success", "data": {...}}

# Receive
plaintext = bob_session.receive_message(msg)
```

### 2. Ghost Mode (Perfect Invisibility)

```python
from matp import GhostMode

key = b"shared_secret_key_32_bytes_long!"
alice = GhostMode(key=key)
bob = GhostMode(key=key)

# Send hidden in GitHub API response
cover = alice.send_invisible("Secret data", service="github")
# Returns: {"id": 123456, "login": "user", "bio": "<encrypted>", ...}

# Receive
message = bob.receive_invisible(cover)
```

### 3. Fast Ghost Mode (Speed + Invisibility)

```python
from matp import FastGhostMode

key = b"benchmark_key_32_bytes_padding!!"
alice = FastGhostMode(key=key)
bob = FastGhostMode(key=key)

# 0.01ms latency, perfect invisibility
cover = alice.send("Fast secret message")
message = bob.receive(cover)
```

### 4. Dead Drop Protocol

```python
from matp import DeadDropProtocol

key = b"dead_drop_key_32_bytes_padding!!"
dead_drop = DeadDropProtocol(key=key)

# Alice drops message (no direct connection to Bob)
location = dead_drop.drop_message("secret_spot_42", "The eagle has landed")

# Bob picks up later
message = dead_drop.pickup_message(location)
```

### 5. Group Messaging

```python
from matp import MatryoshkaGroupManager

# Create users
alice = MatryoshkaGroupManager("alice")
bob = MatryoshkaGroupManager("bob")

# Alice creates group
group = alice.create_group("team", "Secret Team")

# Bob joins
invite = group.export_invite()
bob.join_group(invite)

# Alice sends invisible group message
msg = alice.send_to_group("team", "Meeting at 3pm!")
# Returns: {"status": "success", "data": {...}}  # Looks like normal API

# Bob receives
received = bob.receive_group_message(msg)
print(received['message'])  # "Meeting at 3pm!"
```

### 6. Quantum-Resistant Crypto (Optional)

```python
from matp import quantum

qc = quantum.get_quantum_crypto()

# Generate post-quantum keypair
keypair = qc.generate_kem_keypair()

# Encapsulate shared secret
kem_ct = qc.kem_encapsulate(keypair.public_key)

# Decapsulate
shared_secret = qc.kem_decapsulate(keypair.secret_key, kem_ct.ciphertext)
```

## 📚 API Reference

### Core Classes

- `MatryoshkaProtocol` - 1-to-1 encrypted messaging
- `GhostMode` - Steganographic messaging
- `FastGhostMode` - High-performance steganography
- `DeadDropProtocol` - Asynchronous message drops
- `MatryoshkaGroupManager` - Group messaging
- `quantum.get_quantum_crypto()` - Post-quantum cryptography

## ⚠️ Disclaimer

Research prototype. Use for educational purposes. Not audited for production use.

## 📄 License

Apache 2.0

## 👤 Author

Sangeet Sharma
