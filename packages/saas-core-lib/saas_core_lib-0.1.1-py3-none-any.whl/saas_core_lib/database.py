"""
Database Connection Management
SQLAlchemy 2.0+ async engine with connection pooling
"""

from functools import lru_cache
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession, 
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import logging

from .config import get_settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """SQLAlchemy declarative base"""
    pass

class DatabaseManager:
    """Database connection and session manager"""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
    
    @property
    def engine(self) -> AsyncEngine:
        """Get or create async engine"""
        if self._engine is None:
            self._engine = create_async_engine(
                self.settings.DATABASE_URL,
                pool_size=self.settings.DB_POOL_SIZE,
                max_overflow=self.settings.DB_MAX_OVERFLOW,
                pool_timeout=self.settings.DB_POOL_TIMEOUT,
                pool_recycle=self.settings.DB_POOL_RECYCLE,
                echo=self.settings.DB_ECHO,
                poolclass=NullPool if self.settings.ENVIRONMENT == "testing" else None,
            )
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker:
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._session_factory
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session (async context manager)"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close database engine"""
        if self._engine:
            await self._engine.dispose()

# Global instance
_database_manager: Optional[DatabaseManager] = None

@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Get cached database manager instance"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session

async def create_tables():
    """Create all database tables"""
    db_manager = get_database_manager()
    await db_manager.create_tables()

