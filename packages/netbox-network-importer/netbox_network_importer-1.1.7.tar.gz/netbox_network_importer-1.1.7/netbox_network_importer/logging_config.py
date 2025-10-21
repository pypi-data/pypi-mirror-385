"""
Centralized logging configuration using loguru with best practices.
Replaces the mixed stdlib logging + loguru approach with pure loguru.
"""

import sys
import logging
from pathlib import Path
from loguru import logger
from typing import Dict, Any


class LoguruConfig:
    """Centralized loguru configuration manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_level = config.get("config", {}).get("LOG_LEVEL", "INFO")
        self.log_dir = config.get("config", {}).get("LOG_DIR", "logs")
        self.suppress_connection_errors = config.get("config", {}).get("SUPPRESS_CONNECTION_ERRORS", True)
        
    def setup_logging(self, enable_file_logging: bool = True, enable_console_logging: bool = True):
        """Setup loguru with all configurations"""
        
        # Remove default loguru handler
        logger.remove()
        
        # Setup console logging
        if enable_console_logging:
            logger.add(
                sys.stderr,
                level=self.log_level,
                format=self._format_console_message,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )
        
        # Setup file logging
        if enable_file_logging:
            self._setup_file_logging()
        
        # Setup third-party library logging suppression
        self._setup_third_party_logging()
        
        # Intercept standard library logging
        self._intercept_stdlib_logging()
        
        logger.info(f"Logging configured - Level: {self.log_level}, Suppress connection errors: {self.suppress_connection_errors}")
    
    def _get_console_format(self) -> str:
        """Get console log format with structured data"""
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    def _get_file_format(self) -> str:
        """Get file log format (more detailed) with structured data"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
    
    def _format_console_message(self, record):
        """Custom formatter that includes extra data in a readable format"""
        # Base format
        format_str = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Add extra fields if they exist
        extra = record.get("extra", {})
        if extra:
            extra_pairs = []
            for key, value in extra.items():
                if key not in ['component', 'logger_name']:  # Skip internal keys
                    extra_pairs.append(f"{key}={value}")
            if extra_pairs:
                format_str += f" <cyan>[{', '.join(extra_pairs)}]</cyan>"
        
        format_str += "\n"
        return format_str
    
    def _format_file_message(self, record):
        """Custom file formatter that includes extra data in a readable format"""
        # Base format for files (no colors)
        format_str = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
        
        # Add extra fields if they exist
        extra = record.get("extra", {})
        if extra:
            extra_pairs = []
            for key, value in extra.items():
                if key not in ['component', 'logger_name']:  # Skip internal keys
                    extra_pairs.append(f"{key}={value}")
            if extra_pairs:
                format_str += f" [{', '.join(extra_pairs)}]"
        
        format_str += "\n"
        return format_str
    
    def _setup_file_logging(self):
        """Setup file logging with rotation"""
        log_path = Path(self.log_dir)
        
        if not log_path.exists():
            try:
                log_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Cannot create log directory {log_path}: {e}")
                return
        
        if not log_path.is_dir():
            logger.error(f"Log path {log_path} is not a directory")
            return
        
        # Main log file
        logger.add(
            log_path / "output.log",
            level=self.log_level,
            format=self._format_file_message,
            rotation="5 MB",
            retention="10 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
        
        # Error-only log file
        logger.add(
            log_path / "errors.log",
            level="ERROR",
            format=self._format_file_message,
            rotation="5 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
        
        # Debug log file (only if debug level)
        if self.log_level == "DEBUG":
            logger.add(
                log_path / "debug.log",
                level="DEBUG",
                format=self._format_file_message,
                rotation="10 MB",
                retention="3 days",
                compression="gz",
                backtrace=True,
                diagnose=True,
            )
    
    def _setup_third_party_logging(self):
        """Configure third-party library logging levels"""
        
        # Base library configurations (always applied)
        base_configs = {
            "urllib3.connectionpool": "INFO",
            "pyats": "WARNING", 
            "git": "INFO",
            "genie": "INFO",
            "nornir.core": "WARNING",
            "genie.utils.summary": "INFO",
            "genie.ops.base.maker": "INFO",
            "blib2to3.pgen2.driver": "INFO",
            "paramiko.transport": "WARNING",
            "netmiko": "WARNING",
            "napalm": "WARNING",
            "pyats.contrib.creators.netbox": "ERROR",
        }
        
        # Connection error suppression (applied conditionally)
        if self.suppress_connection_errors:
            connection_configs = {
                "napalm.pyIOSXR.iosxr": "CRITICAL",
                "napalm.iosxr.iosxr": "CRITICAL", 
                "napalm.pyIOSXR": "CRITICAL",
                "napalm.iosxr": "CRITICAL",
                "ncclient": "CRITICAL",
                "ncclient.transport": "CRITICAL",
                "ncclient.transport.session": "CRITICAL",
                "ncclient.operations": "CRITICAL",
            }
            base_configs.update(connection_configs)
        
        # Apply all configurations
        for logger_name, level in base_configs.items():
            logging.getLogger(logger_name).setLevel(getattr(logging, level))
            
        if not self.suppress_connection_errors:
            logger.info("Connection error suppression disabled - verbose networking logs enabled")
    
    def _intercept_stdlib_logging(self):
        """Intercept standard library logging and redirect to loguru"""
        
        class InterceptHandler(logging.Handler):
            def emit(self, record: logging.LogRecord):
                # Skip loguru internal messages
                if record.name.startswith('loguru'):
                    return
                
                # Get corresponding Loguru level
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno
                
                # Get caller frame
                frame, depth = sys._getframe(6), 6
                while frame and frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1
                
                # Log to loguru with context
                logger.opt(depth=depth, exception=record.exc_info).log(
                    level, record.getMessage()
                )
        
        # Replace root logger handler
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        
        # Remove handlers from all existing loggers
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True


def setup_logging(config: Dict[str, Any], enable_file_logging: bool = True, enable_console_logging: bool = True):
    """
    Main function to setup logging configuration
    
    Args:
        config: Configuration dictionary
        enable_file_logging: Enable file logging
        enable_console_logging: Enable console logging
    """
    loguru_config = LoguruConfig(config)
    loguru_config.setup_logging(enable_file_logging, enable_console_logging)


# Context managers for temporary log level changes
class LogLevel:
    """Context manager for temporary log level changes"""
    
    def __init__(self, level: str):
        self.level = level
        self.original_handlers = []
    
    def __enter__(self):
        # Store current handlers
        self.original_handlers = logger._core.handlers.copy()
        
        # Remove all handlers and add new ones with different level
        logger.remove()
        logger.add(sys.stderr, level=self.level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original handlers
        logger.remove()
        for handler_id, handler in self.original_handlers.items():
            logger.add(handler._sink, **handler._kwargs)


# Specialized loggers for different components
def get_component_logger(component_name: str):
    """Get a logger bound to a specific component"""
    return logger.bind(component=component_name)


# Network operation specific logging
class NetworkLogger:
    """Specialized logger for network operations with context"""
    
    def __init__(self, host: str, operation: str):
        self.logger = logger.bind(host=host, operation=operation)
        self.host = host
        self.operation = operation
    
    def start_operation(self):
        """Log operation start"""
        self.logger.info(f"Starting {self.operation} for {self.host}")
    
    def success(self, message: str = ""):
        """Log successful operation"""
        self.logger.success(f"{self.operation} completed successfully for {self.host}: {message}")
    
    def error(self, error: Exception, message: str = ""):
        """Log operation error"""
        self.logger.error(f"{self.operation} failed for {self.host}: {message}", exception=error)
    
    def warning(self, message: str):
        """Log operation warning"""
        self.logger.warning(f"{self.operation} warning for {self.host}: {message}")


# Example usage patterns
if __name__ == "__main__":
    # Example configuration
    example_config = {
        "config": {
            "LOG_LEVEL": "INFO",
            "LOG_DIR": "logs",
            "SUPPRESS_CONNECTION_ERRORS": True
        }
    }
    
    # Setup logging
    setup_logging(example_config)
    
    # Basic logging
    logger.info("Application started")
    
    # Component-specific logging
    napalm_logger = get_component_logger("napalm")
    napalm_logger.info("NAPALM connection established")
    
    # Network operation logging
    net_logger = NetworkLogger("192.168.1.1", "interface_sync")
    net_logger.start_operation()
    net_logger.success("10 interfaces synchronized")
    
    # Temporary log level change
    with LogLevel("DEBUG"):
        logger.debug("This debug message will be shown")
    
    logger.debug("This debug message will be filtered out")
