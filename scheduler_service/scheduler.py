import logging
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler_service.jobs import trigger_forecast

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.add_job(trigger_forecast, "interval", hours=24)  # запуск каждый день
scheduler.start()

logger.info("Планировщик запущен")
