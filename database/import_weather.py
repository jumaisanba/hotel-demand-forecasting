from meteostat import Point, Daily, Stations
from datetime import datetime
from shared.db import get_session_sync
from shared.models import City, Weather, Hotel
import pandas as pd

# Инициализация сессии
session = get_session_sync()

start = datetime(2015, 7, 1)
end = datetime(2017, 8, 31)

# Получаем все города, привязанные к отелям
cities = session.query(City).join(Hotel).distinct().all()

# Получаем уже существующие записи погоды (city_id + date) только за нужный период
existing = session.query(Weather.city_id, Weather.date) \
    .filter(Weather.date.between(start.date(), end.date())) \
    .all()

existing_set = {(city_id, date) for city_id, date in existing}

weather_records = []

for city in cities:
    lat = float(city.latitude)
    lon = float(city.longitude)
    point = Point(lat, lon)

    # Поиск ближайшей станции
    stations = Stations().nearby(lat, lon).inventory('daily')
    station = stations.fetch(1)

    if station.empty:
        print(f"Нет подходящих станций для {city.name}")
        continue

    station_id = station.index[0]
    station_name = station.iloc[0]['name']
    print(f"Загружаем для: {city.name} → {station_id} ({station_name})")

    df = Daily(point, start, end).fetch().reset_index()

    for _, row in df.iterrows():
        day = row["time"].date()
        key = (city.id, day)
        if key in existing_set:
            continue

        weather = Weather(
            city_id=city.id,
            date=day,
            temp_avg=row.get("tavg"),
            precipitation=row.get("prcp"),
            wind_speed=row.get("wspd"),
            weather_desc=""
        )
        weather_records.append(weather)

session.add_all(weather_records)
session.commit()
print(f"Загружено {len(weather_records)} строк погоды.")
