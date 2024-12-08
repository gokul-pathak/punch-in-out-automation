import psutil
import time
import threading
import smtplib
import logging
from datetime import datetime
from typing import Dict, List
from email.mime.text import MIMEText
from prometheus_client import start_http_server, Counter, Gauge
from config.settings import MonitoringConfig

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.metrics = {
            'punch_in_success': Counter('punch_in_success_total', 'Successful punch-ins'),
            'punch_in_failure': Counter('punch_in_failure_total', 'Failed punch-ins'),
            'punch_out_success': Counter('punch_out_success_total', 'Successful punch-outs'),
            'punch_out_failure': Counter('punch_out_failure_total', 'Failed punch-outs'),
            'system_memory': Gauge('system_memory_usage', 'System memory usage'),
            'system_cpu': Gauge('system_cpu_usage', 'System CPU usage'),
            'active_threads': Gauge('active_threads', 'Number of active threads')
        }
        
        # Start Prometheus metrics server
        start_http_server(8000)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _monitoring_loop(self):
        while True:
            try:
                self._collect_system_metrics()
                self._check_system_health()
                time.sleep(MonitoringConfig.METRICS_INTERVAL)
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                self._send_alert(f"Monitoring system error: {str(e)}")

    def _collect_system_metrics(self):
        """Collect system metrics"""
        self.metrics['system_memory'].set(psutil.virtual_memory().percent)
        self.metrics['system_cpu'].set(psutil.cpu_percent())
        self.metrics['active_threads'].set(threading.active_count())

    def _check_system_health(self):
        """Check system health and send alerts if needed"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        if (cpu_usage > MonitoringConfig.PERFORMANCE_THRESHOLD * 100 or 
            memory_usage > MonitoringConfig.PERFORMANCE_THRESHOLD * 100 or 
            disk_usage > MonitoringConfig.PERFORMANCE_THRESHOLD * 100):
            self._send_alert(
                f"System resources critical!\n"
                f"CPU: {cpu_usage}%\n"
                f"Memory: {memory_usage}%\n"
                f"Disk: {disk_usage}%"
            )

    def _send_alert(self, message: str):
        """Send alert email"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = 'Punch Automation System Alert'
            msg['From'] = MonitoringConfig.ALERT_EMAIL
            msg['To'] = MonitoringConfig.ALERT_EMAIL

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(MonitoringConfig.ALERT_EMAIL, 'your_app_password')
                server.send_message(msg)
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

    def record_punch_attempt(self, operation: str, success: bool):
        """Record punch operation metrics"""
        if operation == 'in':
            if success:
                self.metrics['punch_in_success'].inc()
            else:
                self.metrics['punch_in_failure'].inc()
        elif operation == 'out':
            if success:
                self.metrics['punch_out_success'].inc()
            else:
                self.metrics['punch_out_failure'].inc()