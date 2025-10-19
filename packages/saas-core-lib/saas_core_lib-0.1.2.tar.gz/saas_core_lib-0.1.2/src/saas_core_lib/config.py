"""
Application Configuration
Environment variables and settings management
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="Authentication Service", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(default="Firestore Replacement - Multi-Site Auth", description="Application description")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    
    # API
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    
    DATABASE_URL: Optional[str] = Field(default=None, description="PostgreSQL database URL")
    SAAS_DATABASE_URL: Optional[str] = Field(default=None, description="SAAS PostgreSQL database URL")
    TENANT_TEMPLATE_DATABASE_URL: Optional[str] = Field(default=None, description="Tenant Template PostgreSQL database URL")
    AUTH_DATABASE_URL: Optional[str] = Field(default=None, description="Auth PostgreSQL database URL")
    
    DB_POOL_SIZE: int = Field(default=10, description="Database pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Database pool recycle time")
    DB_ECHO: bool = Field(default=False, description="Database echo SQL queries")
    
    # Redis
    REDIS_HOST: Optional[str] = Field(default=None, description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    REDIS_STATE_DB: int = Field(default=0, description="Redis state database")
    REDIS_CACHE_DB: int = Field(default=1, description="Redis cache database")
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis pool size")
    REDIS_CONTAINER_NAME: str = Field(default="auth_redis", description="Redis container name")
    REDIS_NETWORK: str = Field(default="auth_network", description="Redis network")
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(default="https://elastic.soorgla.com", description="Elasticsearch URL")
    ELASTICSEARCH_USERNAME: Optional[str] = Field(default=None, description="Elasticsearch username")
    ELASTICSEARCH_PASSWORD: Optional[str] = Field(default=None, description="Elasticsearch password")
    ES_INDEX_PREFIX: str = Field(default="auth", description="Elasticsearch index prefix")
    ES_TIMEOUT: int = Field(default=30, description="Elasticsearch timeout")
    ES_MAX_RETRIES: int = Field(default=3, description="Elasticsearch max retries")

    # JWT
    JWT_SECRET: Optional[str] = Field(default=None, description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRE_DAYS: int = Field(default=7, description="JWT access token expire days")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=43200, description="Refresh token expire minutes")
    JWT_AUDIENCE: str = Field(default="auth-service", description="JWT audience")
    JWT_ISSUER: str = Field(default="auth-service", description="JWT issuer")
    TENANT_TOKEN_EXPIRE_MINUTES: int = Field(default=43200, description="Tenant token expire minutes")
 
    
  
    # Security & CORS
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], description="Allowed hosts")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3330", "http://127.0.0.1:3330"], description="CORS allowed origins")
    CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], description="CORS allowed methods")
    CORS_HEADERS: List[str] = Field(default=["*"], description="CORS allowed headers")
        
    PAYMENT_ENCRYPTION_KEY: Optional[str] = Field(default="Z3Vlc3N0X3BheW1lbnRfa2V5X2Zvcl9kZXYxMjM0NTY3ODkwMTIzNA==", description="Payment encryption key (base64 encoded 32-byte key)")
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_BURST: int = Field(default=10, description="Rate limit burst")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    LOG_FORMAT: str = Field(default="json", description="Log format")
    LOG_TO_ES: bool = Field(default=True, description="Log to Elasticsearch")
    LOG_TO_FILE: bool = Field(default=False, description="Log to file")
    LOG_FILE_PATH: str = Field(default="logs/auth-service.log", description="Log file path")
    LOG_DIRECTORY: str = Field(default="logs", description="Log directory")
    # Site Management
    DEFAULT_SITE_ID: str = Field(default="default", description="Default site ID")
    SITE_DOMAIN_DETECTION: bool = Field(default=True, description="Site domain detection")
    SITE_HEADER_NAME: str = Field(default="X-Site-ID", description="Site header name")
    
    # Performance
    MAX_REQUEST_SIZE: int = Field(default=10485760, description="Max request size in bytes")
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout in seconds")
    
    # Development
    AUTO_RELOAD: bool = Field(default=True, description="Auto reload in development")
    UVICORN_WORKERS: int = Field(default=1, description="Uvicorn workers")
    UVICORN_HOST: str = Field(default="0.0.0.0", description="Uvicorn host")
    UVICORN_PORT: int = Field(default=8080, description="Uvicorn port")
    
    # Migration & Seeding
    RUN_MIGRATIONS: bool = Field(default=True, description="Run migrations on startup")
    SEED_DATA: bool = Field(default=True, description="Seed initial data")
    SEED_ADMIN_EMAIL: str = Field(default="admin@example.com", description="Seed admin email")
    SEED_ADMIN_PASSWORD: str = Field(default="admin123", description="Seed admin password")
    
    # ip info token
    IP_INFO_TOKEN: str = Field(default="", description="Ip info token")
    
    # Eposta
    SMTP_HOST: str = Field(default="", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SMTP_USE_TLS: bool = Field(default=True, description="SMTP use TLS")
    SMTP_USE_SSL: bool = Field(default=False, description="SMTP use SSL")
    EMAIL_FROM: str = Field(default="", description="Email from")
    SUPPORT_EMAIL: str = Field(default="support@example.com", description="Support email address")
    LOGO_URL: str = Field(default="", description="URL for the logo in emails")
    VERIFICATION_CODE_EXPIRE_MINUTES: int = Field(default=15, description="Email verification code expiration in minutes")
    PASSWORD_RESET_CODE_EXPIRE_MINUTES: int = Field(default=15, description="Password reset code expiration in minutes")
    
    # Minio
    MINIO_ENDPOINT: str = Field(default="", description="Minio endpoint")
    MINIO_ROOT_USER: str = Field(default="", description="Minio root user")
    MINIO_ROOT_PASSWORD: str = Field(default="", description="Minio root password")
    MINIO_BUCKET_NAME: str = Field(default="", description="Minio bucket name")
    MINIO_PUBLIC_URL: str = Field(default="", description="Minio public URL")
    
    # RECAPTCHA
    RECAPTCHA_ENABLED: bool = Field(default=False, description="Enable/disable reCAPTCHA")
    RECAPTCHA_PROJECT_ID: str = Field(default="", description="Google Cloud Project ID for reCAPTCHA Enterprise")
    RECAPTCHA_SITE_KEY: str = Field(default="", description="Recaptcha site key for Enterprise")
    RECAPTCHA_SCORE_THRESHOLD: float = Field(default=0.7, description="reCAPTCHA score threshold for blocking requests")
    GOOGLE_RECAPTCHA_API_KEY: str = Field(default="", description="Google reCAPTCHA API key for client-side integration")
    TEST_RECAPTCHA_SITE_KEY: str = Field(default="6LeLy9IrAAAAAMtT20zpU4HAwEUVKMtEM0iIxTkG", description="Test recaptcha site key")
    TEST_RECAPTCHA_SECRET_KEY: str = Field(default="6LeLy9IrAAAAAFAFpsnc-hUEoW4rjjBQrTgo6U9n", description="Test recaptcha secret key")
    
    # URLs
    FRONTEND_URL: str = Field(default="http://localhost:3330", description="Frontend URL")
    BACKEND_URL: str = Field(default="http://localhost:8150", description="Backend URL")
    
    # OAuth Settings
    GOOGLE_OAUTH_CLIENT_ID: str = Field(default="", description="Google OAuth client ID")
    GOOGLE_OAUTH_CLIENT_SECRET: str = Field(default="", description="Google OAuth client secret")
    MICROSOFT_OAUTH_CLIENT_ID: str = Field(default="", description="Microsoft OAuth client ID")
    MICROSOFT_OAUTH_CLIENT_SECRET: str = Field(default="", description="Microsoft OAuth client secret")
    GITHUB_OAUTH_CLIENT_ID: str = Field(default="", description="GitHub OAuth client ID")
    GITHUB_OAUTH_CLIENT_SECRET: str = Field(default="", description="GitHub OAuth client secret")
    HASHUB_API_KEY: str = Field(default="hh_live_62e6dbc416cf7760d22db26fc5e0d31c", description="Hashub API key for OAuth")
    # ElasticSearh index names
    ES_PRODUCT_INDEX: str = Field(default="ecommerce_products_live", description="Elasticsearch product index name")
    ES_PRODUCT_ANALYTICS_INDEX: str = Field(default="analytics-stream-*", description="Elasticsearch product analytics index name")
    ES_PRODUCT_ANALYTICS_HOURLY_INDEX: str = Field(default="analytics_summary_product_hourly", description="Elasticsearch product analytics hourly index name")
    ES_PRODUCT_ANALYTICS_DAILY_INDEX: str = Field(default="analytics_summary_product_daily", description="Elasticsearch product analytics daily index name")
    ES_PRODUCT_ANALYTICS_MONTHLY_INDEX: str = Field(default="analytics_summary_product_monthly", description="Elasticsearch product analytics monthly index name")
    ES_ARCHIVE_PRODUCT_INDEX: str = Field(default="ecommerce_products_archive", description="Elasticsearch archive product index name")
    # Pydantic v2+ ayarı: .env dosyasındaki ekstra değişkenleri görmezden gel
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()