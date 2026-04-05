import logging

from apscheduler.schedulers.background import BackgroundScheduler

from scheduler.jobs import run_forecast_job

logger = logging.getLogger(__name__)

def start_scheduler() -> BackgroundScheduler:
    job_scheduler = BackgroundScheduler()
    job_scheduler.add_job(
        run_forecast_job,
        trigger="interval",
        hours=24,
        id="daily_forecast",
        replace_existing=True,
    )
    job_scheduler.start()
    logger.info("Job scheduler started")
    return job_scheduler