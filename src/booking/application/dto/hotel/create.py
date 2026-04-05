from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CreateHotelData:
    """Данные для создания отеля."""

    name: str
    is_city_hotel: bool


@dataclass(slots=True, frozen=True)
class HotelDto:
    """DTO отеля."""

    id: int
    name: str
    is_city_hotel: bool
    api_key: str
