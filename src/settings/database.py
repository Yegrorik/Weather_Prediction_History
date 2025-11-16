from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
import redis

from .config import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession ,expire_on_commit=False)

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True