import logging
from datetime import datetime

import httpx

from scheduler.config import scheduler_config
#from shared.db import get_sync_session

logger = logging.getLogger(__name__)


def run_forecast_job():
    logger.info("[%s] Запуск задачи trigger_forecast()", datetime.now())
    #session = get_sync_session()

    try:
        # TODO: заменить на динамическое получение из БД
        hotel_ids = [1]
        logger.info("[%s] Найдены отели: %s", datetime.now(), hotel_ids)
    except Exception as e:
        logger.error("[%s] Ошибка при получении hotel_id: %s", datetime.now(), e)
        return

    today = datetime.utcnow().date()
    target_date = min(today, scheduler_config.max_data_date)

    for hotel_id in hotel_ids:
        for has_deposit in [False]:
            payload = {
                "hotel_id": hotel_id,
                "target_date": target_date.isoformat(),
                "has_deposit": has_deposit,
            }

            try:
                response = httpx.post(
                    f"{scheduler_config.router_url}/prediction/run-prediction",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info(
                        "[%s] Прогноз получен: hotel_id=%s, has_deposit=%s",
                        datetime.now(), hotel_id, has_deposit
                    )
                else:
                    logger.error(
                        "[%s] Ошибка от ROUTER %s: %s",
                        datetime.now(), response.status_code, response.text
                    )
            except Exception as e:
                logger.error("[%s] Ошибка при отправке запроса: %s", datetime.now(), e)
