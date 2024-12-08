import os
from typing import Dict, Any
from datetime import time
import json
import cryptography.fernet
import base64

class SecurityConfig:
    SECRET_KEY = base64.b64encode(os.urandom(32)).decode()
    ENCRYPTION_KEY = base64.b64encode(os.urandom(32)).decode()
    
    @classmethod
    def get_cipher(cls):
        return cryptography.fernet.Fernet(cls.ENCRYPTION_KEY.encode())

class ScheduleConfig:
    # Morning window
    MORNING_START = time(8, 30)  # 8:30 AM
    MORNING_END = time(11, 30)   # 11:30 AM
    
    # Evening window
    EVENING_START = time(17, 0)  # 5:00 PM
    EVENING_END = time(19, 30)   # 7:30 PM
    
    # Check interval in minutes
    CHECK_INTERVAL = 10
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 300  # 5 minutes

class NetworkConfig:
    PING_TIMEOUT = 2
    MAX_PING_RETRIES = 3
    NETWORK_TIMEOUT = 10
    ALLOWED_IP_RANGES = [
        '192.168.1.0/24',
        '10.0.0.0/24'
    ]

class MonitoringConfig:
    ALERT_EMAIL = "admin@example.com"
    METRICS_INTERVAL = 300  # 5 minutes
    HEALTH_CHECK_INTERVAL = 60  # 1 minute
    PERFORMANCE_THRESHOLD = 0.8  # 80%