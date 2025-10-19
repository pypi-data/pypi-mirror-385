# SAAS Core Library

Common core library for all microservices in the SAAS platform.

## Features

- **Database Management**: SQLAlchemy 2.0+ async engine with connection pooling
- **Redis Client**: Async Redis client with state and cache databases  
- **Elasticsearch**: Centralized Elasticsearch client management
- **Security**: JWT token management, password hashing, API key handling
- **Logging**: Structured logging with service-specific loggers
- **Response Handling**: Standardized API response formats
- **Configuration**: Environment-based configuration management

## Installation

```bash
pip install saas-core-lib
```

## Usage

### Database

```python
from saas_core_lib import get_db_session, create_tables

# Get database session
async with get_db_session() as session:
    # Your database operations
    pass

# Create all tables
await create_tables()
```

### Redis

```python
from saas_core_lib import get_redis_client

# Get Redis client
redis_client = await get_redis_client()
await redis_client.set("key", "value")
```

### Security

```python
from saas_core_lib import hash_password, verify_password, create_access_token

# Hash password
hashed = hash_password("my_password")

# Verify password
is_valid = verify_password("my_password", hashed)

# Create JWT token
token = create_access_token({"user_id": "123"})
```

### Response Handling

```python
from saas_core_lib import create_success_response, create_error_response, ErrorCode

# Success response
return create_success_response("User created successfully", {"user_id": "123"})

# Error response
return create_error_response("User not found", ErrorCode.NOT_FOUND, 404)
```

### Logging

```python
from saas_core_lib import get_logger, LogLevel, setup_logging

# Setup logging for service
setup_logging("my-service", LogLevel.INFO)

# Get logger
logger = get_logger("my-service")
logger.info("Application started")
```

## Configuration

Set environment variables in `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# Redis  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=password

# Elasticsearch
ELASTICSEARCH_URL=https://localhost:9200
ELASTICSEARCH_USERNAME=user
ELASTICSEARCH_PASSWORD=pass

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

## License

MIT License