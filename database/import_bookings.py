import pandas as pd
from sqlalchemy.orm import Session
from shared.models import Booking, Hotel
from shared.db import get_session_sync
from datetime import date

df = pd.read_csv("database/hotel_bookings.csv")

# Подключение к БД
session: Session = get_session_sync()

# Получаем id отелей
hotels = {h.name: h for h in session.query(Hotel).all()}  # допустим имена 'Hotel A', 'Hotel B'

# Предобработка
def make_date(row):
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return date(int(row['arrival_date_year']),
                month_map[row['arrival_date_month']],
                int(row['arrival_date_day_of_month']))

bookings = []
df['market_segment'] = df['market_segment'].fillna('Undefined')
df['distribution_channel'] = df['distribution_channel'].fillna('Undefined')

df[["adults", "children", "babies",
    "stays_in_weekend_nights", "stays_in_week_nights",
    "lead_time", "booking_changes", "adr"]] = df[[
        "adults", "children", "babies",
        "stays_in_weekend_nights", "stays_in_week_nights",
        "lead_time", "booking_changes", "adr"
    ]].fillna(0)


for _, row in df.iterrows():
    # Пропуск некорректных записей
    if row["adults"] + row["children"] + row["babies"]== 0:
        continue

    if row["stays_in_weekend_nights"] + row["stays_in_week_nights"]== 0:
        continue

    arrival = make_date(row)

    total_guests = int(row["adults"]) + int(row["children"]) + int(row["babies"])
    total_nights = int(row["stays_in_weekend_nights"]) + int(row["stays_in_week_nights"])


    is_cancel = bool(row["is_canceled"])
    has_deposit = row["deposit_type"] != "No Deposit"

    hotel_name = "Hotel A" if row["hotel"] == "City Hotel" else "Hotel B"
    hotel = hotels.get(hotel_name)
    if not hotel:
        continue

    booking = Booking(
        hotel_id=hotel.id,
        arrival_date=arrival,
        lead_time=int(row["lead_time"]),
        adr=float(row["adr"]),
        total_guests=total_guests,
        total_nights=total_nights,
        booking_changes=int(row["booking_changes"]),
        has_deposit=has_deposit,
        is_cancellation=is_cancel,
        market_segment=row["market_segment"],
        distribution_channel=row["distribution_channel"],
        reserved_room_type=row["reserved_room_type"],
        day_of_week=arrival.weekday()
    )
    bookings.append(booking)

session.add_all(bookings)
session.commit()
print(f"Загружено {len(bookings)} записей.")
