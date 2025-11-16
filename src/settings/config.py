import os
from pydantic_settings import BaseSettings, SettingsConfigDict

import logging
import json
import sys
from datetime import datetime

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    WEATHER_API_KEY : str
    BASE_WEATHER_URL : str

    NUMBER_OF_REQUESTS : int

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env"
        )
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text',
                           'filename', 'funcName', 'levelname', 'levelno', 'lineno',
                           'module', 'msecs', 'msg', 'name', 'pathname', 'process',
                           'processName', 'relativeCreated', 'stack_info', 'thread',
                           'threadName'] and not key.startswith('_'):
                log_entry[key] = value

        return json.dumps(log_entry, indent=2, ensure_ascii=False)


logger = logging.getLogger(__name__)
logger.handlers = []

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())

logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False