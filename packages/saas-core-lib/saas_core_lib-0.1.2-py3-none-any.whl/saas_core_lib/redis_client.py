"""
Redis Connection Management
State store and cache with dual database support
"""

import asyncio
import logging
from functools import lru_cache
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis

from .config import get_settings, Settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Manages Redis connection pools and clients for state and cache."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.state_pool: Optional[ConnectionPool] = None
        self.cache_pool: Optional[ConnectionPool] = None
        self.redis_state: Optional[Redis] = None
        self.redis_cache: Optional[Redis] = None

    async def initialize(self) -> None:
        """Creates connection pools and Redis clients."""
        if self.state_pool is not None:
            logger.info("Redis connections already initialized.")
            return

        redis_url = f"redis://:{self.settings.REDIS_PASSWORD}@{self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}"
        
        logger.info("Initializing Redis connection pools...")
        
        try:
            self.state_pool = ConnectionPool.from_url(
                redis_url,
                db=self.settings.REDIS_STATE_DB,
                max_connections=self.settings.REDIS_POOL_SIZE,
                decode_responses=True,
                encoding="utf-8"
            )
            self.cache_pool = ConnectionPool.from_url(
                redis_url,
                db=self.settings.REDIS_CACHE_DB,
                max_connections=self.settings.REDIS_POOL_SIZE,
                decode_responses=True,
                encoding="utf-8"
            )
            
            self.redis_state = redis.Redis(connection_pool=self.state_pool)
            self.redis_cache = redis.Redis(connection_pool=self.cache_pool)
            
            # Test connections
            await self.redis_state.ping()
            await self.redis_cache.ping()
            
            logger.info("✅ Redis connections initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis connections: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Closes connections and disconnects from pools."""
        if self.redis_state:
            await self.redis_state.close()
        if self.redis_cache:
            await self.redis_cache.close()
        if self.state_pool:
            await self.state_pool.disconnect()
        if self.cache_pool:
            await self.cache_pool.disconnect()
        logger.info("✅ Redis connections closed.")

    def get_state_client(self) -> Redis:
        """Get Redis state store connection."""
        if not self.redis_state:
            raise RuntimeError("Redis state store not initialized")
        return self.redis_state

    def get_cache_client(self) -> Redis:
        """Get Redis cache connection."""
        if not self.redis_cache:
            raise RuntimeError("Redis cache not initialized")
        return self.redis_cache

    async def check_connection(self) -> bool:
        """Check Redis connections health."""
        try:
            if not self.redis_state or not self.redis_cache:
                return False
            await self.redis_state.ping()
            await self.redis_cache.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

# Singleton instance for application-wide use
redis_manager = RedisManager(get_settings())

# --- FastAPI Dependency Functions (maintaining backward compatibility) ---

async def init_redis() -> None:
    """Initialize Redis connections using the manager."""
    await redis_manager.initialize()

async def close_redis() -> None:
    """Close Redis connections using the manager."""
    await redis_manager.close()

def get_redis_state() -> Redis:
    """Dependency to get Redis state store connection."""
    return redis_manager.get_state_client()

def get_redis_cache() -> Redis:
    """Dependency to get Redis cache connection."""
    return redis_manager.get_cache_client()

def get_redis() -> Redis:
    """Dependency to get Redis state connection (backward compatibility)."""
    return redis_manager.get_state_client()

def get_redis_client() -> Redis:
    """Dependency to get Redis cache connection (backward compatibility)."""
    return redis_manager.get_cache_client()

async def check_redis_connection() -> bool:
    """Check Redis connections health."""
    return await redis_manager.check_connection()


# --- Standalone Test Function ---

async def _run_tests():
    """Runs a series of tests to validate Redis connectivity and operations."""
    print("🚀 Running RedisManager tests...")
    
    # Configure logging for test output
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # 1. Initialize
        print("\n--- 1. Initializing Redis Manager ---")
        await init_redis()
        
        state_client = get_redis_state()
        cache_client = get_redis_cache()
        
        # 2. Check Connection
        print("\n--- 2. Health Check ---")
        is_healthy = await check_redis_connection()
        print(f"Connection Health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        if not is_healthy:
            raise RuntimeError("Redis connection check failed.")

        # 3. State DB Operations
        print("\n--- 3. State DB Operations (DB {}) ---".format(get_settings().REDIS_STATE_DB))
        state_key = "test:state:user_session:123"
        state_value = '{"user_id": "123", "role": "admin"}'
        await state_client.set(state_key, state_value, ex=60)
        print(f"SET state key '{state_key}' with 60s TTL.")
        retrieved_state = await state_client.get(state_key)
        print(f"GET state key '{state_key}': {retrieved_state}")
        print(f"Verification: {'✅ OK' if retrieved_state == state_value else '❌ Fail'}")
        
        # 4. Cache DB Operations
        print("\n--- 4. Cache DB Operations (DB {}) ---".format(get_settings().REDIS_CACHE_DB))
        cache_key = "test:cache:product:xyz"
        cache_value = '{"name": "FastAPI Course", "price": 100}'
        await cache_client.set(cache_key, cache_value, ex=60)
        print(f"SET cache key '{cache_key}' with 60s TTL.")
        retrieved_cache = await cache_client.get(cache_key)
        print(f"GET cache key '{cache_key}': {retrieved_cache}")
        print(f"Verification: {'✅ OK' if retrieved_cache == cache_value else '❌ Fail'}")

    except Exception as e:
        logger.error(f"❌ An error occurred during Redis tests: {e}", exc_info=True)
    finally:
        # 5. Close Connections
        print("\n--- 5. Closing Connections ---")
        await close_redis()
        print("\n✅ All tests completed.")


# Global Redis manager instance

@lru_cache()
def get_redis_manager() -> RedisManager:
    """Get cached Redis manager instance"""
    return RedisManager(get_settings())

if __name__ == "__main__":
    # Note: Ensure your .env file is correctly configured for these tests to run.
    asyncio.run(_run_tests())