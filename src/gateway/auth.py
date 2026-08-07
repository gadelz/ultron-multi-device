"""
Token-based authentication for ULTron Gateway
Supports JWT and API key authentication
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import json

class AuthService:
    """Authentication service for device-to-gateway communication"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv("ULTRON_SECRET_KEY", secrets.token_hex(32))
        self.tokens: Dict[str, Dict] = {}
        self.token_ttl = timedelta(hours=24)
    
    def generate_device_token(self, device_id: str) -> str:
        """Generate a secure token for a device"""
        token = secrets.token_hex(32)
        self.tokens[token] = {
            "device_id": device_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.token_ttl,
            "scope": ["wake_unlock", "play_media", "answer_call"]
        }
        return token
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate a device token"""
        if token not in self.tokens:
            return None
        
        token_data = self.tokens[token]
        if token_data["expires_at"] < datetime.utcnow():
            del self.tokens[token]
            return None
        
        return token_data
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a device token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    def hash_password(self, password: str) -> str:
        """Hash a password with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{password}{self.secret_key}".encode()).hexdigest()
        return f"{salt}${hashed}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against hash"""
        try:
            salt, stored_hash = hashed.split("$")
            computed_hash = hashlib.sha256(f"{salt}{password}{self.secret_key}".encode()).hexdigest()
            return computed_hash == stored_hash
        except:
            return False
    
    def get_device_by_token(self, token: str) -> Optional[str]:
        """Get device ID from token"""
        token_data = self.validate_token(token)
        return token_data["device_id"] if token_data else None
