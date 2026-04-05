from booking.application.domain.api_key import generate_api_key
from booking.application.dto.hotel.create import CreateHotelData
from booking.application.ports.repositories import IHotelRepository
from booking.infrastructure.db.models import Hotel
from shared.errors import NotFoundError


class HotelService:
    """Сервис для работы с доменной логикой отелей."""

    def __init__(self, hotel_repo: IHotelRepository):
        self._hotel_repo = hotel_repo

    async def create(self, hotel_data: CreateHotelData) -> Hotel:
        """Создаёт отель и генерирует для него уникальный API-ключ."""
        api_key = await self._generate_unique_api_key()
        hotel = await self._hotel_repo.create(
            name=hotel_data.name,
            is_city_hotel=hotel_data.is_city_hotel,
            api_key=api_key,
        )
        return hotel

    async def regenerate_api_key(self, hotel_id: int) -> str:
        """Перегенерирует API-ключ для существующего отеля."""
        await self._require_hotel(hotel_id)

        new_key = await self._generate_unique_api_key()
        await self._hotel_repo.update_api_key(hotel_id, new_key)
        return new_key

    async def _generate_unique_api_key(self, max_attempts=5) -> str:
        """Генерирует уникальный API-ключ с ограничением на число попыток."""
        for _ in range(max_attempts):
            candidate = generate_api_key()
            if not await self._hotel_repo.exists_by_api_key(candidate):
                return candidate
        raise RuntimeError("Failed to generate unique API key after multiple attempts")

    async def _require_hotel(self, hotel_id: int) -> Hotel:
        """Возвращает отель или выбрасывает NotFoundError."""
        hotel = await self._hotel_repo.get_by_id(hotel_id)
        if hotel is None:
            raise NotFoundError("Hotel not found")
        return hotel
