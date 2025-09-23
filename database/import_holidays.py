import holidays
from datetime import datetime
from shared.db import get_session_sync
from shared.models import Holiday
from sqlalchemy import and_

# Период
start = datetime(2015, 7, 1).date()
end = datetime(2017, 8, 31).date()

# Подключение к БД
session = get_session_sync()

# Список праздников Португалии
pt_holidays = holidays.country_holidays('PT', years=[2015, 2016, 2017])

# Фильтрация по датам
filtered = [(d, name) for d, name in pt_holidays.items() if start <= d <= end]

# Получение уже существующих записей на эти даты по региону Portugal
existing = session.query(Holiday.date).filter(
    and_(Holiday.date >= start, Holiday.date <= end, Holiday.region == "Portugal")
).all()
existing_dates = {e[0] for e in existing}

# Добавление новых
new_records = []
for date_, name in filtered:
    if date_ not in existing_dates:
        new_records.append(Holiday(
            date=date_,
            holiday_name=name,
            is_national=True,
            region="Portugal"
        ))

session.add_all(new_records)
session.commit()
print(f"Загружено {len(new_records)} праздников Португалии.")
