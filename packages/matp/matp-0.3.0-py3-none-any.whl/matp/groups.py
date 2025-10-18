#!/usr/bin/env python3
"""
Matryoshka Groups - Group messaging with Fractal Group Ratchet

Combines Fractal Group Ratchet with Matryoshka steganography.
"""

import json
import time
import base64
from typing import Dict, List, Optional
from .fractal_ratchet import FractalGroupRatchet
from .protocol import MatryoshkaProtocol


class MatryoshkaGroup:
    """Production-ready group chat with invisible encryption."""
    
    def __init__(self, group_id: str, group_name: str, creator_id: str):
        self.group_id = group_id
        self.group_name = group_name
        self.creator_id = creator_id
        self.created_at = time.time()
        
        self.ratchet = FractalGroupRatchet()
        self.group_seed = self.ratchet.group_seed
        
        self.members: List[str] = [creator_id]
        self.admins: List[str] = [creator_id]
        self.message_history: List[dict] = []
    
    def get_group_info(self) -> dict:
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "creator": self.creator_id,
            "members": self.members,
            "admins": self.admins,
            "member_count": len(self.members),
            "fingerprint": self.ratchet.get_fingerprint(),
            "created_at": self.created_at
        }
    
    def add_member(self, user_id: str, is_admin: bool = False):
        if user_id not in self.members:
            self.members.append(user_id)
            if is_admin:
                self.admins.append(user_id)
    
    def remove_member(self, user_id: str, requester_id: str) -> bool:
        if requester_id not in self.admins:
            return False
        if user_id in self.members:
            self.members.remove(user_id)
            if user_id in self.admins:
                self.admins.remove(user_id)
        return True
    
    def send_message(self, sender_id: str, message: str, use_steganography: bool = True) -> dict:
        encrypted_envelope = self.ratchet.encrypt_for_group(message)
        
        group_message = {
            "type": "group_message",
            "group_id": self.group_id,
            "sender": sender_id,
            "timestamp": time.time(),
            "encrypted": encrypted_envelope
        }
        
        self.message_history.append({
            "sender": sender_id,
            "timestamp": group_message["timestamp"],
            "layer": encrypted_envelope["layer"]
        })
        
        if use_steganography:
            payload = base64.b64encode(json.dumps(group_message).encode()).decode()
            return {
                "status": "success",
                "data": {
                    "user_id": 12345,
                    "session_token": payload,
                    "preferences": {"theme": "dark", "lang": "en"},
                    "timestamp": int(time.time())
                },
                "meta": {"version": "2.1.0", "server": "api-01"}
            }
        return group_message
    
    def receive_message(self, ghost_msg_data: dict) -> dict:
        if "data" in ghost_msg_data and "session_token" in ghost_msg_data["data"]:
            encoded = ghost_msg_data["data"]["session_token"]
            encrypted = base64.b64decode(encoded)
            decrypted_json = encrypted.decode('utf-8')
        else:
            decrypted_json = json.dumps(ghost_msg_data)
        
        group_message = json.loads(decrypted_json)
        
        if group_message["group_id"] != self.group_id:
            raise ValueError("Message not for this group")
        
        plaintext = self.ratchet.decrypt_from_group(group_message["encrypted"])
        
        return {
            "sender": group_message["sender"],
            "message": plaintext,
            "timestamp": group_message["timestamp"],
            "group_id": self.group_id,
            "group_name": self.group_name
        }
    
    def export_invite(self, from_layer: Optional[int] = None) -> dict:
        if from_layer is None:
            from_layer = self.ratchet.message_counter
        
        session = self.ratchet.export_session(from_layer=from_layer)
        
        return {
            "type": "group_invite",
            "group_id": self.group_id,
            "group_name": self.group_name,
            "creator": self.creator_id,
            "members": self.members,
            "session": session,
            "invited_at": time.time()
        }
    
    def rotate_group_seed(self, requester_id: str) -> Optional[bytes]:
        if requester_id not in self.admins:
            return None
        new_seed = self.ratchet.rotate_seed()
        self.group_seed = new_seed
        return new_seed


class MatryoshkaGroupManager:
    """Manage multiple groups for a user."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.groups: Dict[str, MatryoshkaGroup] = {}
        self.private_key, self.public_key = MatryoshkaProtocol.generate_keypair()
        self.peer_sessions: Dict[str, MatryoshkaProtocol] = {}
    
    def create_group(self, group_id: str, group_name: str) -> MatryoshkaGroup:
        group = MatryoshkaGroup(group_id, group_name, self.user_id)
        self.groups[group_id] = group
        return group
    
    def join_group(self, invite_data: dict) -> MatryoshkaGroup:
        group = MatryoshkaGroup(
            invite_data["group_id"],
            invite_data["group_name"],
            invite_data["creator"]
        )
        group.ratchet.import_session(invite_data["session"])
        group.group_seed = group.ratchet.group_seed
        group.members = invite_data["members"]
        group.members.append(self.user_id)
        self.groups[group.group_id] = group
        return group
    
    def send_to_group(self, group_id: str, message: str) -> dict:
        if group_id not in self.groups:
            raise ValueError(f"Not in group: {group_id}")
        return self.groups[group_id].send_message(self.user_id, message)
    
    def receive_group_message(self, ghost_msg_data: dict) -> dict:
        for group in self.groups.values():
            try:
                return group.receive_message(ghost_msg_data)
            except (ValueError, KeyError):
                continue
        raise ValueError("Message not for any of your groups")
    
    def invite_to_group(self, group_id: str, invitee_id: str, invitee_public_key) -> dict:
        if group_id not in self.groups:
            raise ValueError(f"Not in group: {group_id}")
        
        group = self.groups[group_id]
        shared_secret = MatryoshkaProtocol.derive_shared_secret(self.private_key, invitee_public_key)
        peer_session = MatryoshkaProtocol(key=shared_secret)
        self.peer_sessions[invitee_id] = peer_session
        
        invite = group.export_invite()
        invite_msg = peer_session.send_message(json.dumps(invite), use_steganography=True)
        group.add_member(invitee_id)
        return invite_msg.cover_data
    
    def get_all_groups(self) -> List[dict]:
        return [group.get_group_info() for group in self.groups.values()]
    
    def leave_group(self, group_id: str):
        if group_id in self.groups:
            del self.groups[group_id]
