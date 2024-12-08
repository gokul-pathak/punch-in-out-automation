import hmac
import hashlib
import base64
import logging
import ipaddress
from typing import Optional
from datetime import datetime, timedelta
from config.settings import SecurityConfig, NetworkConfig

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.cipher = SecurityConfig.get_cipher()
        self._failed_attempts = {}
        self._blocked_ips = set()

    def encrypt_credentials(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt_credentials(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            return self.cipher.decrypt(decoded_data).decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise

    def validate_ip_address(self, ip: str) -> bool:
        """Validate if IP is in allowed range"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for allowed_range in NetworkConfig.ALLOWED_IP_RANGES:
                if ip_obj in ipaddress.ip_network(allowed_range):
                    return True
            return False
        except ValueError:
            return False

    def record_failed_attempt(self, ip: str):
        """Record failed login attempt"""
        current_time = datetime.now()
        if ip not in self._failed_attempts:
            self._failed_attempts[ip] = []
        
        self._failed_attempts[ip].append(current_time)
        
        # Check if IP should be blocked
        recent_failures = [
            t for t in self._failed_attempts[ip]
            if t > current_time - timedelta(minutes=30)
        ]
        
        if len(recent_failures) >= 5:
            self._blocked_ips.add(ip)
            logger.warning(f"IP {ip} blocked due to multiple failed attempts")

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self._blocked_ips

    def generate_session_token(self, user_id: str) -> str:
        """Generate secure session token"""
        timestamp = datetime.now().timestamp()
        message = f"{user_id}:{timestamp}"
        return hmac.new(
            SecurityConfig.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()