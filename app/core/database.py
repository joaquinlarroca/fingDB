"""
Database Configuration for fingDB

This file configures the async database connection using SQLAlchemy.

Key Concepts:
- AsyncIO: Python's library for writing concurrent code using async/await
- AsyncSession: SQLAlchemy session for async operations
- create_async_engine: Creates an async database engine
- Connection Pooling: Manages multiple database connections efficiently
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import DATABASE_URL

# ============================================================================
# ASYNC DATABASE ENGINE
# ============================================================================

# Create async engine for database operations
# In production, this would connect to PostgreSQL
# The DATABASE_URL comes from config.py (environment variables)
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create async session factory
# This is used to create database sessions for each request
# expire_on_commit=False keeps objects usable after commit
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    """
    FastAPI dependency that provides an async database session.

    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...

    The session is automatically closed after the request.
    """
    async with AsyncSession(engine) as session:
        yield session


# ============================================================================
# DECLARATIVE BASE
# ============================================================================

# Base class for all ORM models
# All models in app/models/ inherit from this
Base = declarative_base()
