import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI

from scheduler.runner import start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan: запуск планировщика")
    sched = start_scheduler()
    try:
        yield
    finally:
        logger.info("Lifespan: остановка планировщика")
        sched.shutdown(wait=False)


app = FastAPI(title="Scheduler Service API", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Scheduler Service is running"}
