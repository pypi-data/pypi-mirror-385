"""
Matryoshka Protocol (MATP) - Invisible Secure Messaging

Complete package with:
- MatryoshkaProtocol: 1-to-1 encrypted messaging
- GhostMode: Perfect invisibility (ε → 0)
- FastGhostMode: Speed + invisibility
- DeadDropProtocol: No direct communication
- ServiceRotation: Traffic diversity
- FractalGroupRatchet: O(1) group encryption
- MatryoshkaGroup: Invisible group chat
- MatryoshkaGroupManager: Multi-group management

License: Apache 2.0
Author: Sangeet Sharma
"""

__version__ = "0.3.0"
__author__ = "Sangeet Sharma"
__license__ = "Apache 2.0"

from .protocol import MatryoshkaProtocol, GhostMessage
from .ghost import GhostMode, DeadDropProtocol, ServiceRotation
from .ghost_fast import FastGhostMode
from .fractal_ratchet import FractalGroupRatchet
from .groups import MatryoshkaGroup, MatryoshkaGroupManager
from .innocence_proof import InnocenceProof, generate_innocence_proof, verify_innocence_proof

__all__ = [
    "MatryoshkaProtocol",
    "GhostMessage",
    "GhostMode",
    "FastGhostMode",
    "DeadDropProtocol",
    "ServiceRotation",
    "FractalGroupRatchet",
    "MatryoshkaGroup",
    "MatryoshkaGroupManager",
    "InnocenceProof",
    "generate_innocence_proof",
    "verify_innocence_proof",
]
