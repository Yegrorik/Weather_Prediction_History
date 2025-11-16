from sqlalchemy import text

from ..settings.database import redis_client, async_session_maker
from .weather_tools import weather_tool
from ..settings.config import logger


async def chek_db():
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

async def chek_redis():
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False

async def chek_api():
    try:
        await weather_tool.get_weather("Brest")
        return True
    except Exception as e:
        logger.warning(f"External API health check failed: {str(e)}")
        return False