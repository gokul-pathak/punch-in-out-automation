import re
import subprocess
import logging
from typing import List, Tuple, Dict
import socket
from datetime import datetime

logger = logging.getLogger(__name__)

class NetworkManager:
    OFFLINE_MSG = 'Destination host unreachable'
    ONLINE_ECHO_FAILED_MSG = 'Request timed out.'
    ONLINE_ECHO_SUCCESS_MSG = '0% loss'
    MAC_ADDR_PATTERN = '([-0-9a-f]{17})'
    PING_TIMEOUT = 2  # seconds

    @staticmethod
    def ping_device(ip_addr: str) -> bool:
        """
        Ping device and return True if online, False if offline
        """
        try:
            # Create the ping command based on OS
            if subprocess.os.name == 'nt':  # Windows
                ping_cmd = ['ping', '-n', '1', '-w', str(NetworkManager.PING_TIMEOUT * 1000), ip_addr]
            else:  # Linux/Unix
                ping_cmd = ['ping', '-c', '1', '-W', str(NetworkManager.PING_TIMEOUT), ip_addr]
            
            result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8')
            
            return (NetworkManager.ONLINE_ECHO_SUCCESS_MSG in output or 
                   NetworkManager.ONLINE_ECHO_FAILED_MSG in output)
        
        except subprocess.SubprocessError as e:
            logger.error(f"Error pinging device {ip_addr}: {str(e)}")
            return False

    @staticmethod
    def get_mac_address(ip_addr: str) -> str:
        """
        Get MAC address for given IP address
        """
        try:
            if subprocess.os.name == 'nt':  # Windows
                arp_cmd = ['arp', '-a', ip_addr]
            else:  # Linux/Unix
                arp_cmd = ['arp', '-n', ip_addr]
            
            result = subprocess.run(arp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8')
            
            mac_matches = re.findall(NetworkManager.MAC_ADDR_PATTERN, output)
            return mac_matches[0] if mac_matches else None
            
        except (subprocess.SubprocessError, IndexError) as e:
            logger.error(f"Error getting MAC address for {ip_addr}: {str(e)}")
            return None

    @staticmethod
    def get_online_offline_devices(ip_addr_list: List[str]) -> Tuple[List[str], List[str]]:
        """
        Categorize devices into online and offline lists
        """
        online_ips = []
        offline_ips = []
        
        for ip in ip_addr_list:
            try:
                if NetworkManager.ping_device(ip):
                    online_ips.append(ip)
                    logger.info(f"Device {ip} is online")
                else:
                    offline_ips.append(ip)
                    logger.info(f"Device {ip} is offline")
            
            except Exception as e:
                logger.error(f"Error checking device {ip}: {str(e)}")
                offline_ips.append(ip)
        
        return online_ips, offline_ips
