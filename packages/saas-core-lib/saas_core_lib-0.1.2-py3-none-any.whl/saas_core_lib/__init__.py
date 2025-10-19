"""
SAAS Core Library
Common utilities and configurations for microservices
"""

__version__ = "0.1.2"
__author__ = "Hasan Bahadır"
__email__ = "hasan@hashub.dev"

# Core imports
from .config import Settings, get_settings
from .database import (
    DatabaseManager,
    get_database_manager,
    get_db_session,
    create_tables,
    Base
)
from .redis_client import (
    RedisManager,
    get_redis_manager,
    get_redis_client
)
from .elasticsearch import (
    ElasticsearchManager,
    get_elasticsearch_manager,
    get_es_client
)
from .security import (
    SecurityManager,
    get_security_manager,
    create_access_token,
    verify_token,
    hash_password,
    verify_password
)
from .logging.logger import (
    get_logger,
    setup_logging,
    LogLevel,
    tenant_activity_logger,
    security_events_logger,
    application_logs_logger,
    bot_traffic_logger,
    analytics_logger,
    auth_events_logger,
    api_metrics_logger,
    system_logger
)
from .response.response_handler import (
    StandardResponse,
    ResponseStatus,
    ErrorCode,
    create_success_response,
    create_error_response,
    create_validation_error_response
)

# All exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Config
    "Settings",
    "get_settings",
    
    # Database
    "DatabaseManager",
    "get_database_manager", 
    "get_db_session",
    "create_tables",
    "Base",
    
    # Redis
    "RedisManager",
    "get_redis_manager",
    "get_redis_client",
    
    # Elasticsearch
    "ElasticsearchManager",
    "get_elasticsearch_manager",
    "get_es_client",
    
    # Security
    "SecurityManager",
    "get_security_manager",
    "create_access_token",
    "verify_token", 
    "hash_password",
    "verify_password",
    
    # Logging
    "get_logger",
    "setup_logging",
    "LogLevel",
    "tenant_activity_logger",
    "security_events_logger",
    "application_logs_logger",
    "bot_traffic_logger",
    "analytics_logger",
    "auth_events_logger",
    "api_metrics_logger",
    "system_logger",
    
    # Response handling
    "StandardResponse",
    "ResponseStatus",
    "ErrorCode",
    "create_success_response",
    "create_error_response",
    "create_validation_error_response",
]