from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import os

import time
from contextlib import asynccontextmanager

from .service.points import weather_router
from .service.healthers import chek_db, chek_api, chek_redis
from .settings.config import logger

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Application starting up")
    yield

    logger.info("Application shutting down")

app = FastAPI(lifespan=lifespan)

current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/health")
async def chek_health():
    start_time = time.time()

    db_health = await chek_db()
    redis_health = await chek_redis()
    api_health = await chek_api()

    status = "healthy" if all([db_health, redis_health]) else "unhealthy"

    total_time = time.time() - start_time

    logger.info(
        "health_check_completed",
        extra={
                "status": status,
                "database": "connected" if db_health else "disconnected",
                "redis": "connected" if redis_health else "disconnected",
                "external_api": "reachable" if api_health else "unreachable",
                "response_time": f"{total_time:.3f}s"
            }
    )

    if status == "healthy":
        return {
            "status": status,
            "Data Base" : "connected",
            "Redis" : "connected",
            "External Api" : "reachable" if api_health else "unreachable"
        }
    else:
        raise HTTPException(status_code=503,
                            detail = {
                                "status" : status,
                                "Data Base" : "connected" if db_health else "unconnected",
                                "Redis" : "connected" if redis_health else "unreachable",
                                "External Api" : "reachable" if api_health else "unreachable"
                            })

app.include_router(weather_router)