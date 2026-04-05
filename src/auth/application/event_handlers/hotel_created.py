from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.roles import UserRole


class HotelCreatedEventHandler:
    """Обрабатывает события, связанные со связью пользователь-отель."""

    def __init__(
            self,
            uow: IUnitOfWork,
    ) -> None:
        self._uow = uow

    async def handle(
            self,
            *,
            event_id: str,
            hotel_id: int,
            owner_user_id: int,
            role: UserRole,
    ) -> None:
        """Создаёт связь user_hotel по событию hotel.created."""
        async with self._uow:
            if await self._uow.processed_events.exists(event_id):
                return

            exists = await self._uow.users_hotels.get(
                user_id=owner_user_id,
                hotel_id=hotel_id,
            )
            if not exists:
                await self._uow.users_hotels.create(
                    user_id=owner_user_id,
                    hotel_id=hotel_id,
                    role=role,
                )

            await self._uow.processed_events.add(
                event_id=event_id,
                event_type="hotel.created",
            )
            await self._uow.commit()
