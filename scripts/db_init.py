"""
Скрипт для инициализации схемы БД.
"""

import logging
from shared.db import engine
from shared.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init():
    Base.metadata.create_all(bind=engine)
    logger.info("Схема БД создана")


if __name__ == "__main__":
    init()