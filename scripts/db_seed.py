"""
Скрипт для пересоздания схемы БД и загрузки тестовых данных.

Используется только для разработки и демонстрации.
"""

import logging
from shared.db import get_session_sync, engine, Base
from shared.models import City, Hotel, Holiday,Weather, Booking, Prediction
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init():
    # Пересоздание схемы
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = get_session_sync()

    # Города
    city1 = City(name="Moscow", latitude=55.7558, longitude=37.6173, region="Moscow")
    city2 = City(name="Sochi", latitude=43.5855, longitude=39.7231, region="Krasnodar")
    city3 = City(name="Kazan", latitude=55.7963, longitude=49.1088, region="Tatarstan")
    session.add_all([city1, city2, city3])
    session.flush()

    # Отели
    hotel1 = Hotel(name="Hotel A", city=city1, is_city_hotel=True, api_key="f7b9c6a3ef84d05ce3a18b42d7b2f8c0")
    hotel2 = Hotel(name="Hotel B", city=city2, is_city_hotel=False, api_key="9d4fa2f0c7a35e289b3d1f504a0cf15e")
    hotel3 = Hotel(name="Hotel C", city=city3, is_city_hotel=True, api_key="6e3abf3296c4461bb4faed78a9c7c412")
    session.add_all([hotel1, hotel2, hotel3])
    session.flush()

    # Праздники
    holidays = [
        Holiday(date=date(2025, 1, 1), holiday_name="New Year", is_national=True, region="Russia"),
        Holiday(date=date(2025, 3, 8), holiday_name="Women's Day", is_national=True, region="Russia"),
        Holiday(date=date(2025, 5, 9), holiday_name="Victory Day", is_national=True, region="Russia")
    ]
    session.add_all(holidays)

    # Погода
    weathers = [
        Weather(city=city1, date=date(2025, 1, 1), temp_avg=-5, precipitation=3, wind_speed=2.1, weather_desc="Snow"),
        Weather(city=city2, date=date(2025, 1, 1), temp_avg=6, precipitation=1.2, wind_speed=1.0,weather_desc="Cloudy"),
        Weather(city=city3, date=date(2025, 1, 1), temp_avg=-10, precipitation=0, wind_speed=3.0, weather_desc="Clear")
    ]
    session.add_all(weathers)

    # Бронирования
    bookings = [
        Booking(hotel=hotel1, arrival_date=date(2025, 1, 10), lead_time=20, total_guests=2, total_nights=3,
                booking_changes=0, has_deposit=False, is_cancellation=False, market_segment="Online",
                distribution_channel="Direct", reserved_room_type="A", day_of_week=4),
        Booking(hotel=hotel2, arrival_date=date(2025, 1, 15), lead_time=5, total_guests=4, total_nights=2,
                booking_changes=1, has_deposit=True, is_cancellation=False, market_segment="Online",
                distribution_channel="TA", reserved_room_type="B", day_of_week=2),
        Booking(hotel=hotel3, arrival_date=date(2025, 1, 20), lead_time=10, total_guests=1, total_nights=1,
                booking_changes=0, has_deposit=False, is_cancellation=True, market_segment="Corporate",
                distribution_channel="TO", reserved_room_type="C", day_of_week=1),
    ]
    session.add_all(bookings)

    # Прогнозы
    predictions = [
        Prediction(hotel=hotel1, target_date=date(2025, 1, 10), room_type="A", has_deposit=False,
                   distribution_channel="Direct", bookings=15, cancellations=2),
        Prediction(hotel=hotel2, target_date=date(2025, 1, 15), room_type="B", has_deposit=True,
                   distribution_channel="TA", bookings=10, cancellations=1),
        Prediction(hotel=hotel3, target_date=date(2025, 1, 20), room_type="C", has_deposit=False,
                   distribution_channel="TO", bookings=5, cancellations=0)
    ]
    session.add_all(predictions)

    session.commit()
    logger.info("Схема пересоздана и тестовые данные добавлены")

if __name__ == "__main__":
    init()
