from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.settings import settings

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


def get_session() -> AsyncSession:
    return AsyncSessionLocal()


def get_engine():
    return engine
