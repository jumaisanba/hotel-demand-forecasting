from booking.application.dto.hotel.create import CreateHotelData, HotelDto
from booking.application.dto.events import HotelCreatedEvent
from booking.application.dto.outbox import NewOutboxEvent
from booking.application.ports.unit_of_work import IUnitOfWork
from booking.application.services.hotel import HotelService
from booking.infrastructure.db.models import OutboxEvent


async def create_hotel(
        uow: IUnitOfWork,
        data: CreateHotelData,
        owner_user_id: int,
) -> HotelDto:
    async with uow:
        hotel = await HotelService(uow.hotels).create(data)

        event = HotelCreatedEvent.create(
            hotel_id=hotel.id,
            owner_user_id=owner_user_id,
        )

        await uow.outbox.add(
            NewOutboxEvent(
                id=event.event_id,
                event_type=event.event_type,
                routing_key="hotel.created",
                payload=event.to_dict(),
            )
        )

        await uow.commit()
        return HotelDto(
            id=hotel.id,
            name=hotel.name,
            is_city_hotel=hotel.is_city_hotel,
            api_key=hotel.api_key,
        )
