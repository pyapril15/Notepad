"""
Logger - Application logging utility
"""

import logging
from datetime import datetime
from pathlib import Path


class Logger:
    """Application logger"""

    def __init__(self, log_level=logging.INFO):
        self.log_dir = Path.home() / '.modern_notepad' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp
        log_filename = f"notepad_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_file = self.log_dir / log_filename

        # Configure logger
        self.logger = logging.getLogger('ModernNotepad')
        self.logger.setLevel(log_level)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)

        # Console handler (only for warnings and errors by default)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # Cleanup old log files (keep last 30 days)
        self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        """Remove log files older than 30 days"""
        try:
            cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days

            for log_file in self.log_dir.glob('notepad_*.log'):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")

    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)

    def exception(self, message):
        """Log exception with traceback"""
        self.logger.exception(message)

    def log_file_operation(self, operation, file_path, success=True):
        """Log file operation"""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"File operation: {operation} - {file_path} - {status}")

    def log_user_action(self, action, details=None):
        """Log user action"""
        message = f"User action: {action}"
        if details:
            message += f" - {details}"
        self.info(message)

    def log_performance(self, operation, duration):
        """Log performance metrics"""
        self.info(f"Performance: {operation} took {duration:.3f} seconds")

    def log_error_with_context(self, error, context=None):
        """Log error with additional context"""
        message = f"Error: {error}"
        if context:
            message += f" | Context: {context}"
        self.error(message)

    def get_log_file_path(self):
        """Get current log file path"""
        return str(self.log_file)

    def get_recent_logs(self, lines=100):
        """Get recent log entries"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                return log_lines[-lines:] if len(log_lines) > lines else log_lines
        except Exception as e:
            self.error(f"Error reading log file: {e}")
            return []

    def clear_logs(self):
        """Clear current log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('')
            self.info("Log file cleared")
            return True
        except Exception as e:
            self.error(f"Error clearing log file: {e}")
            return False

    def export_logs(self, export_path):
        """Export logs to specified path"""
        try:
            import shutil
            shutil.copy2(self.log_file, export_path)
            self.info(f"Logs exported to: {export_path}")
            return True
        except Exception as e:
            self.error(f"Error exporting logs: {e}")
            return False

    def set_console_log_level(self, level):
        """Set console logging level"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)
                break

    def enable_debug_mode(self):
        """Enable debug mode (show all logs in console)"""
        self.set_console_log_level(logging.DEBUG)
        self.info("Debug mode enabled")

    def disable_debug_mode(self):
        """Disable debug mode (show only warnings and errors in console)"""
        self.set_console_log_level(logging.WARNING)
        self.info("Debug mode disabled")


# Global logger instance
_logger_instance = None


def get_logger():
    """Get global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance


# Convenience functions
def log_info(message):
    get_logger().info(message)


def log_error(message):
    get_logger().error(message)


def log_warning(message):
    get_logger().warning(message)


def log_debug(message):
    get_logger().debug(message)


def log_exception(message):
    get_logger().exception(message)
