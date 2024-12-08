from monitoring.system_monitor import SystemMonitor
from security.security_manager import SecurityManager
from error_handling.error_manager import ErrorManager, retry_on_failure
from config.settings import ScheduleConfig
# ... (previous imports)

class PunchAutomationScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.punch_system = AutomatedPunchSystem()
        self.monitor = SystemMonitor()
        self.security = SecurityManager()
        self.error_manager = ErrorManager()
        self.ip_addresses = self.load_ip_config()

    @retry_on_failure()
    def process_punch_operation(self):
        try:
            current_time = datetime.now().time()
            operation_type = self._determine_operation_type(current_time)
            
            if not operation_type:
                return
            
            online_ips, offline_ips = get_online_offline_devices(self.ip_addresses)
            
            # Validate IPs
            online_ips = [ip for ip in online_ips if self.security.validate_ip_address(ip)]
            offline_ips = [ip for ip in offline_ips if self.security.validate_ip_address(ip)]

            if operation_type == 'PI':
                self._handle_punch_in(online_ips)
            else:
                self._handle_punch_out(offline_ips)

        except Exception as e:
            self.error_manager.handle_error(e, "process_punch_operation")

    def _handle_punch_in(self, online_ips):
        for ip in online_ips:
            try:
                if self.security.is_ip_blocked(ip):
                    logger.warning(f"Skipping blocked IP: {ip}")
                    continue
                
                success = self.punch_system.process_punch_in([ip])
                self.monitor.record_punch_attempt('in', success)
                
                if not success:
                    self.security.record_failed_attempt(ip)
                
            except Exception as e:
                self.error_manager.handle_error(e, f"punch_in_{ip}")

    def _handle_punch_out(self, offline_ips):
        # Similar to _handle_punch_in but for punch out
        pass

    def _determine_operation_type(self, current_time):
        """Determine operation type based on time"""
        if (ScheduleConfig.MORNING_START <= current_time <= ScheduleConfig.MORNING_END):
            return 'PI'
        elif (ScheduleConfig.EVENING_START <= current_time <= ScheduleConfig.EVENING_END):
            return 'PO'
        return None

    def start(self):
        try:
            # Add monitoring job
            self.scheduler.add_job(
                self.monitor._check_system_health,
                'interval',
                seconds=MonitoringConfig.HEALTH_CHECK_INTERVAL
            )

            # Add main punch jobs
            self.scheduler.add_job(
                self.process_punch_operation,
                'cron',
                day_of_week='mon-fri',
                hour='8-11,17-19',
                minute=f'*/{ScheduleConfig.CHECK_INTERVAL}'
            )

            logger.info("Scheduler started successfully")
            self.scheduler.start()