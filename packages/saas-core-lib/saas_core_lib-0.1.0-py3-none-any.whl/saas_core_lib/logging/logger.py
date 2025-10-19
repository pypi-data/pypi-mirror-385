"""
Logger System
Basit ve güvenli logging sistemi - emoji replacement ile Elasticsearch uyumluluğu
"""

import os
import json
import logging
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Dict, Optional, Any
from logging.handlers import RotatingFileHandler

from ..config import get_settings

# Emoji to text mapping for Windows compatibility and Elasticsearch safety
EMOJI_REPLACEMENTS = {
    '🚀': '[ROCKET]',
    '❌': '[ERROR]',
    '✅': '[SUCCESS]',
    '🔍': '[SEARCH]',
    '🏢': '[BUILDING]',
    '🛡️': '[SHIELD]',
    '🤖': '[ROBOT]',
    '🕰️': '[CLOCK]',
    '📋': '[CLIPBOARD]',
    '⚠️': '[WARNING]',
    '🔒': '[LOCK]',
    '🔑': '[KEY]',
    '📊': '[CHART]',
    '🌐': '[GLOBE]',
    '📱': '[MOBILE]',
    '💾': '[DISK]',
    '🔄': '[REFRESH]',
    '⭐': '[STAR]',
    '🎯': '[TARGET]'
}

def clean_emoji(text: str) -> str:
    """Replace emoji characters with text equivalents for safe logging"""
    if not isinstance(text, str):
        return str(text)
    
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        text = text.replace(emoji, replacement)
    return text

def clean_emoji_recursive(obj: Any) -> Any:
    """Recursively clean emojis from nested structures"""
    if isinstance(obj, dict):
        return {k: clean_emoji_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_emoji_recursive(item) for item in obj]
    elif isinstance(obj, str):
        return clean_emoji(obj)
    else:
        return obj

class LogLevel(Enum):
    """Log levels enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

settings = get_settings()

# Log directories
BASE_LOG_DIR = settings.LOG_DIRECTORY
SERVICE_LOG_DIRS = {
    "tenant_activity": f"{BASE_LOG_DIR}/tenant_activity",
    "security_events": f"{BASE_LOG_DIR}/security_events", 
    "application_logs": f"{BASE_LOG_DIR}/application_logs",
    "bot_traffic": f"{BASE_LOG_DIR}/bot_traffic",
    "analytics": f"{BASE_LOG_DIR}/analytics",
    "auth_events": f"{BASE_LOG_DIR}/auth_events",
    "api_metrics": f"{BASE_LOG_DIR}/api_metrics",
    "system": f"{BASE_LOG_DIR}/system"
}

class ServiceLogger:
    """Service-specific logger with JSON formatting"""
    
    def __init__(self, service_name: str, log_dir: str):
        self.service_name = service_name
        self.log_dir = log_dir
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file handler and JSON formatter"""
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger(f"service.{self.service_name}")
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create rotating file handler
        log_file = os.path.join(self.log_dir, f"{self.service_name}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Create JSON formatter
        formatter = ServiceLogFormatter()
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger
    
    def log(self, level: str, message: str, tenant_id: Optional[str] = None, 
            user_id: Optional[str] = None, **kwargs):
        """Log message with structured data"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": level.upper(),
            "message": message,
            "tenant_id": tenant_id,
            "user_id": user_id,
            **kwargs
        }
        
        # Log at appropriate level
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        message = clean_emoji(message)
        self.log("info", message, **kwargs)
    
    def warn(self, message: str, **kwargs):
        """Log warning message"""
        message = clean_emoji(message)
        self.log("warn", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        message = clean_emoji(message)
        self.log("error", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        message = clean_emoji(message)
        self.log("debug", message, **kwargs)


class ServiceLogFormatter(logging.Formatter):
    """Custom JSON formatter for service logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        try:
            # If the message is already JSON, use it directly
            log_data = json.loads(record.getMessage())
            return json.dumps(log_data, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, create structured log entry
            log_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data, ensure_ascii=False)


class CentralLogger:
    """Central logger manager"""
    
    def __init__(self):
        self.loggers: Dict[str, ServiceLogger] = {}
        self._initialize_loggers()
    
    def _initialize_loggers(self):
        """Initialize all service loggers"""
        for service_name, log_dir in SERVICE_LOG_DIRS.items():
            self.loggers[service_name] = ServiceLogger(service_name, log_dir)
    
    def get_logger(self, service_name: str) -> ServiceLogger:
        """Get logger for specific service"""
        if service_name not in self.loggers:
            # Create logger for new service
            log_dir = f"{BASE_LOG_DIR}/{service_name}"
            self.loggers[service_name] = ServiceLogger(service_name, log_dir)
        
        return self.loggers[service_name]
    
    def tenant_activity_logger(self) -> ServiceLogger:
        """Get tenant activity logger"""
        return self.get_logger("tenant_activity")
    
    def security_events_logger(self) -> ServiceLogger:
        """Get security events logger"""
        return self.get_logger("security_events")
    
    def application_logs_logger(self) -> ServiceLogger:
        """Get application logs logger"""
        return self.get_logger("application_logs")
    
    def bot_traffic_logger(self) -> ServiceLogger:
        """Get bot traffic logger"""
        return self.get_logger("bot_traffic")
    
    def analytics_logger(self) -> ServiceLogger:
        """Get analytics logger"""
        return self.get_logger("analytics")
    
    def auth_events_logger(self) -> ServiceLogger:
        """Get auth events logger"""
        return self.get_logger("auth_events")
    
    def api_metrics_logger(self) -> ServiceLogger:
        """Get API metrics logger"""
        return self.get_logger("api_metrics")
    
    def system_logger(self) -> ServiceLogger:
        """Get system logger"""
        return self.get_logger("system")


# Global central logger instance
central_logger = CentralLogger()

# Convenience functions for easy access
@lru_cache()
def tenant_activity_logger() -> ServiceLogger:
    """Get tenant activity logger - kullanımı: tenant_activity_logger().info("message")"""
    return central_logger.tenant_activity_logger()

@lru_cache()
def security_events_logger() -> ServiceLogger:
    """Get security events logger - kullanımı: security_events_logger().error("threat detected")"""
    return central_logger.security_events_logger()

@lru_cache()
def application_logs_logger() -> ServiceLogger:
    """Get application logs logger - kullanımı: application_logs_logger().debug("debug info")"""
    return central_logger.application_logs_logger()

@lru_cache()
def bot_traffic_logger() -> ServiceLogger:
    """Get bot traffic logger - kullanımı: bot_traffic_logger().warn("bot detected")"""
    return central_logger.bot_traffic_logger()

@lru_cache()
def analytics_logger() -> ServiceLogger:
    """Get analytics logger - kullanımı: analytics_logger().info("event tracked")"""
    return central_logger.analytics_logger()

@lru_cache()
def auth_events_logger() -> ServiceLogger:
    """Get auth events logger - kullanımı: auth_events_logger().info("user logged in")"""
    return central_logger.auth_events_logger()

@lru_cache()
def api_metrics_logger() -> ServiceLogger:
    """Get API metrics logger - kullanımı: api_metrics_logger().info("api call")"""
    return central_logger.api_metrics_logger()

@lru_cache()
def system_logger() -> ServiceLogger:
    """Get system logger - kullanımı: system_logger().error("system error")"""
    return central_logger.system_logger()


# Test function
def test_central_logger():
    """Test central logger functionality"""
    print("🧪 Testing Central Logger System...")
    
    # Test tenant activity logger
    tenant_logger = tenant_activity_logger()
    tenant_logger.info(
        "User activity tracked",
        tenant_id="test-tenant-123",
        user_id="user-456",
        action="login",
        resource="user_account"
    )
    print("✅ Tenant activity logged")
    
    # Test security events logger
    security_logger = security_events_logger()
    security_logger.error(
        "Security threat detected",
        tenant_id="test-tenant-123",
        threat_type="brute_force",
        source_ip="203.0.113.42",
        severity="high"
    )
    print("✅ Security event logged")
    
    # Test application logs logger
    app_logger = application_logs_logger()
    app_logger.debug(
        "Application debug info",
        tenant_id="test-tenant-123",
        module="auth_service",
        function="validate_token"
    )
    print("✅ Application log logged")
    
    # Test bot traffic logger
    bot_logger = bot_traffic_logger()
    bot_logger.warn(
        "Bot traffic detected",
        tenant_id="test-tenant-123",
        bot_type="malicious_bot",
        client_ip="203.0.113.43",
        action_taken="blocked"
    )
    print("✅ Bot traffic logged")
    
    # Test analytics logger
    analytics_log = analytics_logger()
    analytics_log.info(
        "Analytics event processed",
        tenant_id="test-tenant-123",
        event_type="page_view",
        user_id="user-789"
    )
    print("✅ Analytics logged")
    
    print("\n📁 Log files created in:")
    for service_name, log_dir in SERVICE_LOG_DIRS.items():
        log_file = os.path.join(log_dir, f"{service_name}.log")
        if os.path.exists(log_file):
            print(f"   - {log_file}")
    
    print("\n✅ Central Logger System Test Completed!")


# Global logger management
_loggers: Dict[str, ServiceLogger] = {}

@lru_cache(maxsize=128)
def get_logger(service_name: str = "application") -> ServiceLogger:
    """Get or create a logger for a service"""
    if service_name not in _loggers:
        log_dir = SERVICE_LOG_DIRS.get(service_name, f"{BASE_LOG_DIR}/{service_name}")
        _loggers[service_name] = ServiceLogger(service_name, log_dir)
    return _loggers[service_name]

def setup_logging(service_name: str = "application", log_level: LogLevel = LogLevel.INFO):
    """Setup logging for a service"""
    logger = get_logger(service_name)
    logger.logger.setLevel(getattr(logging, log_level.value))
    return logger

if __name__ == "__main__":
    test_central_logger()
