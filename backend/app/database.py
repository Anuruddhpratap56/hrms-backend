from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings

# engine = create_async_engine(settings.async_database_url, pool_pre_ping=True)
engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0}
)
SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
