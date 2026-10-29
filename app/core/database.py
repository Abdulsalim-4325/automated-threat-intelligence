from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create async engine for PostgreSQL 16
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
)

# Session factory for dependency injection and background workers
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass

async def get_db() -> AsyncSession:
    """Dependency generator for FastAPI routes to obtain an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
