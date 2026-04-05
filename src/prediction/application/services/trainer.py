import logging
from pathlib import Path
from shutil import copytree

import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset

from prediction.application.services.forecast_data_loader import ForecastDataLoader
from prediction.application.ml.gru_model import GRUForecaster
from prediction.application.ml.model_loader import load_model_config
from prediction.application.ports.unit_of_work import IUnitOfWork
from prediction.application.ml.preprocessing.preprocessor import preprocess_data
from prediction.application.ml.preprocessing.scaling import normalize_data
from prediction.application.ml.preprocessing.sequencing import create_sequences

logger = logging.getLogger(__name__)


def setup_hotel_model_from_base(hotel_id: int) -> None:
    """Копирует базовую модель и конфиг как шаблон для нового отеля."""
    base_path = Path("../../models/base_model")
    hotel_path = Path(f"../models/hotel_{hotel_id}")

    if hotel_path.exists():
        logger.info("Модель для hotel_%s уже существует — пропуск копирования.", hotel_id)
        return

    copytree(base_path, hotel_path)
    logger.info("Базовая модель успешно скопирована для hotel_%s.", hotel_id)


async def _load_training_dataframe(
        hotel_id: int,
        uow: IUnitOfWork,
) -> tuple[pd.DataFrame, object]:
    """
    Загружает данные для обучения модели.

    Возвращает:
        tuple[pd.DataFrame, object]:
            - объединённый DataFrame признаков
            - проекцию отеля
    """
    async with uow:
        loader = ForecastDataLoader(
            bookings=uow.bookings_projection,
            hotels=uow.hotels_projection,
            weather=uow.weather,
            holidays=uow.holidays,
        )

        df_b = await loader.load_bookings(hotel_id)
        df_w = await loader.load_weather(hotel_id)
        df_h = await loader.load_holidays()
        hotel = await loader.get_hotel_projection(hotel_id)

    df = df_b.merge(df_w, left_on="arrival_date", right_on="day", how="left")
    df["is_holiday"] = df["arrival_date"].isin(df_h["day"]).astype(int)
    df["is_city_hotel"] = int(hotel.is_city_hotel)

    return df, hotel


def _train_model_on_dataframe(
        *,
        hotel_id: int,
        df: pd.DataFrame,
        target_col: str,
        window_size: int,
        epochs: int,
        batch_size: int,
) -> None:
    """Обучает модель на заранее подготовленном DataFrame."""
    logger.info("Начало обучения модели для hotel_id=%s", hotel_id)

    config = load_model_config(hotel_id)

    model = GRUForecaster(
        num_numeric_features=len(config["numeric_features"]),
        embedding_sizes={k: tuple(v) for k, v in config["embedding_sizes"].items()},
        hidden_size=config["hidden_size"],
        gru_layers=config["gru_layers"],
        dropout=config["dropout"],
        forecast_horizon=config["forecast_horizon"],
        output_dims=config["output_dims"],
    )

    model_path = Path(f"../models/hotel_{hotel_id}/model.pt")
    if model_path.exists():
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        logger.info("Загружена существующая модель из %s", model_path)
    else:
        logger.warning("Файл весов %s не найден — обучение начнётся с нуля.", model_path)

    logger.info("Предобработка и нормализация данных...")
    df_processed = preprocess_data(df, hotel_id)
    df_scaled = normalize_data(df_processed, hotel_id)

    x_np, y_np = create_sequences(
        df_scaled,
        config["numeric_features"],
        target_col,
        window_size,
    )

    x_tensor = torch.tensor(x_np, dtype=torch.float32)
    y_tensor = torch.tensor(y_np, dtype=torch.float32)

    dataset = TensorDataset(x_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.get("learning_rate", 0.001),
        weight_decay=config.get("weight_decay", 0.0001),
    )
    criterion = torch.nn.MSELoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0

        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        logger.info("Epoch %s/%s — Loss: %.4f", epoch + 1, epochs, avg_loss)

    torch.save(model.state_dict(), model_path)
    logger.info("Модель сохранена: %s", model_path)
    logger.info("Обучение модели для hotel_id=%s завершено успешно.", hotel_id)


async def train_model_for_hotel(
        hotel_id: int,
        uow: IUnitOfWork,
        target_col: str = "bookings",
        window_size: int = 30,
        epochs: int = 10,
        batch_size: int = 32,
) -> None:
    """
    Загружает данные через UoW и обучает модель прогнозирования для указанного отеля.
    """
    logger.info("Загрузка данных бронирований, погоды и праздников для hotel_id=%s...", hotel_id)

    df, _hotel = await _load_training_dataframe(
        hotel_id=hotel_id,
        uow=uow,
    )

    _train_model_on_dataframe(
        hotel_id=hotel_id,
        df=df,
        target_col=target_col,
        window_size=window_size,
        epochs=epochs,
        batch_size=batch_size,
    )
