from datetime import datetime
from shared.db import get_session_sync
from shared.models import Prediction
import numpy as np

# Исторические значения
history = [
    ("2017-07-10", 122, 46), ("2017-07-11", 102, 35), ("2017-07-12", 101, 25),
    ("2017-07-13", 148, 41), ("2017-07-14", 70, 26), ("2017-07-15", 191, 75),
    ("2017-07-16", 98, 28), ("2017-07-17", 125, 47), ("2017-07-18", 87, 23),
    ("2017-07-19", 60, 13), ("2017-07-20", 86, 29), ("2017-07-21", 93, 29),
    ("2017-07-22", 139, 41), ("2017-07-23", 84, 25), ("2017-07-24", 135, 42),
    ("2017-07-25", 87, 25), ("2017-07-26", 95, 32), ("2017-07-27", 104, 40),
    ("2017-07-28", 100, 50), ("2017-07-29", 135, 58), ("2017-07-30", 78, 25),
    ("2017-07-31", 116, 39), ("2017-08-01", 93, 38), ("2017-08-02", 106, 33),
    ("2017-08-03", 123, 44), ("2017-08-04", 97, 28), ("2017-08-05", 80, 29),
    ("2017-08-06", 74, 26), ("2017-08-07", 118, 37), ("2017-08-08", 80, 34),
]

# MAE метрики (1–7 дней и 8–30)
mae = {
    "bookings_1_7": 15.08,
    "cancellations_1_7": 12.82,
    "bookings_8_30": 25.54,
    "cancellations_8_30": 23.78,
}

def generate_predictions():
    predictions = []
    for i, (date_str, true_b, true_c) in enumerate(history):
        day_idx = i + 1
        is_short = day_idx <= 7

        err_b = mae["bookings_1_7"] if is_short else mae["bookings_8_30"]
        err_c = mae["cancellations_1_7"] if is_short else mae["cancellations_8_30"]

        pred_b = max(0, round(np.random.normal(loc=true_b, scale=err_b)))
        pred_c = max(0, round(np.random.normal(loc=true_c, scale=err_c)))

        predictions.append({
            "target_date": datetime.strptime(date_str, "%Y-%m-%d").date(),
            "bookings": pred_b,
            "cancellations": pred_c
        })
    return predictions

def main():
    hotel_id = 1
    has_deposit = False

    with get_session_sync() as db:
        predictions = generate_predictions()

        for entry in predictions:
            record = Prediction(
                hotel_id=hotel_id,
                has_deposit=has_deposit,
                target_date=entry["target_date"],
                bookings=entry["bookings"],
                cancellations=entry["cancellations"]
            )
            db.add(record)
        db.commit()

        print(f"Добавлено {len(predictions)} записей в таблицу predictions.")

if __name__ == "__main__":
    main()
