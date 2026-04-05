import logging
from datetime import timedelta, date

import numpy as np
import pandas as pd
import torch

from prediction.application.services.forecast_data_loader import ForecastDataLoader
from prediction.application.ml.model_loader import load_model_and_config
from prediction.application.ports.unit_of_work import IUnitOfWork
from prediction.application.ml.preprocessing.preprocessor import preprocess_data
from prediction.application.ml.preprocessing.scaling import normalize_data, denormalize_forecast
from shared.errors import (
    ModelConfigError,
    ValidationError,
    ServiceError,
)

logger = logging.getLogger(__name__)


def aggregate_forecast_inputs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Агрегирует входные данные по дате:
    числовые признаки усредняет, категориальные — берёт по моде.
    """
    agg_df = df.groupby("arrival_date").agg(
        {
            col: "mean"
            for col in df.columns
            if col not in [
            "arrival_date",
            "day_of_week",
            "market_segment_enc",
            "distribution_channel_enc",
            "reserved_room_type_enc",
        ]
        }
    ).reset_index()

    for cat_col in [
        "day_of_week",
        "market_segment_enc",
        "distribution_channel_enc",
        "reserved_room_type_enc",
    ]:
        mode_vals = df.groupby("arrival_date")[cat_col].agg(
            lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        )
        agg_df[cat_col] = mode_vals.values

    return agg_df


async def process_inputs_for_model(
        hotel_id: int,
        uow: IUnitOfWork,
        config: dict,
        target_date: date,
        has_deposit: bool,
) -> np.ndarray:
    """
    Загружает и подготавливает входные данные для модели.

    Returns:
        np.ndarray: массив входных признаков формы [horizon, num_features].
    """
    logger.info(
        "Подготовка входных данных: hotel_id=%s, target_date=%s, has_deposit=%s",
        hotel_id,
        target_date,
        has_deposit,
    )

    async with uow:
        loader = ForecastDataLoader(
            bookings=uow.bookings_projection,
            hotels=uow.hotels_projection,
            weather=uow.weather,
            holidays=uow.holidays,
        )

        try:
            df_b = await loader.load_bookings(hotel_id)
            df_b = df_b[df_b["has_deposit"] == has_deposit]

            df_w = await loader.load_weather(hotel_id)
            df_h = await loader.load_holidays()
            hotel = await loader.get_hotel_projection(hotel_id)
        except Exception as exc:
            logger.exception("Ошибка при загрузке данных для прогноза: %s", exc)
            raise ServiceError("Ошибка загрузки данных для прогноза") from exc

    df_b["arrival_date"] = pd.to_datetime(df_b["arrival_date"], errors="coerce")
    df_w["day"] = pd.to_datetime(df_w["day"], errors="coerce")
    df_h["day"] = pd.to_datetime(df_h["day"], errors="coerce")

    df_b.drop(
        columns=["booking_ref", "updated_at", "hotel_id", "payload_hash", "source_updated_at"],
        inplace=True,
        errors="ignore",
    )
    df_h.drop(columns=["region"], inplace=True, errors="ignore")

    df = df_b.merge(
        df_w,
        left_on="arrival_date",
        right_on="day",
        how="left",
        suffixes=("", "_weather"),
    )

    start_date = target_date - timedelta(days=29)
    df = df[
        (df["arrival_date"].dt.date >= start_date)
        & (df["arrival_date"].dt.date <= target_date)
        ]
    if df.empty:
        raise ValidationError(f"Нет данных о бронированиях {start_date} – {target_date}")

    df["is_holiday"] = df["arrival_date"].isin(df_h["day"]).astype(int)
    df["is_city_hotel"] = int(hotel.is_city_hotel)

    df = preprocess_data(df, hotel_id)
    df = normalize_data(df, hotel_id)

    numeric_features = config["numeric_features"]
    categorical_features = config["categorical_features"]

    missing = [
        col
        for col in numeric_features + categorical_features
        if col not in df.columns
    ]
    if missing:
        raise ModelConfigError(f"В данных отсутствуют признаки: {missing}")

    df = aggregate_forecast_inputs(df)

    if len(df) < config["forecast_horizon"]:
        raise ValidationError(
            f"Недостаточно дней: {len(df)} < {config['forecast_horizon']}"
        )

    df = df.sort_values("arrival_date")

    numeric_ordered = df[numeric_features].values
    categorical_ordered = df[categorical_features].values
    x_combined = np.concatenate([numeric_ordered, categorical_ordered], axis=1)

    return x_combined[-config["forecast_horizon"]:]


async def run_forecast_for_hotel(
        hotel_id: int,
        uow: IUnitOfWork,
        target_date: date,
        has_deposit: bool,
) -> dict:
    """
    Запускает прогноз для отеля.
    """
    logger.info(
        "Запуск прогноза: hotel_id=%s, target_date=%s, has_deposit=%s",
        hotel_id,
        target_date,
        has_deposit,
    )

    model, config = load_model_and_config(hotel_id)

    x = await process_inputs_for_model(
        hotel_id=hotel_id,
        uow=uow,
        config=config,
        target_date=target_date,
        has_deposit=has_deposit,
    )

    expected_dim = config["num_numeric_features"] + len(config["categorical_features"])
    if x.shape[1] != expected_dim:
        raise ModelConfigError(
            f"Ожидалось {expected_dim} признаков, получено {x.shape[1]}"
        )

    num_feats = config["numeric_features"]
    cat_feats = config["categorical_features"]

    x_numeric = x[:, :len(num_feats)]
    x_categorical = x[:, len(num_feats):]

    x_cat_dict = {
        feat: torch.tensor(x_categorical[:, idx], dtype=torch.long).unsqueeze(0)
        for idx, feat in enumerate(cat_feats)
    }
    x_numeric_tensor = torch.tensor(x_numeric, dtype=torch.float32).unsqueeze(0)

    try:
        with torch.no_grad():
            y_pred = model(x_numeric_tensor, x_cat_dict).squeeze(0).numpy()
    except Exception as exc:
        raise ServiceError(f"Ошибка при выполнении прогноза: {exc}") from exc

    y_pred = denormalize_forecast(y_pred, hotel_id)

    forecast = [
        {
            "date": (target_date + timedelta(days=i)).isoformat(),
            "bookings": int(round(book)),
            "cancellations": int(round(cancel)),
        }
        for i, (book, cancel) in enumerate(y_pred)
    ]

    logger.info("Прогноз завершён: %s дней", len(forecast))

    return {
        "hotel_id": hotel_id,
        "target_date": target_date.isoformat(),
        "forecast": forecast,
    }
