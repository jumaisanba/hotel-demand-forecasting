from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.roles import UserRole
from auth.application.services import UserHotelService


async def assign_owner(uow: IUnitOfWork, user_id: int, hotel_id: int) -> None:
    async with uow:
        await UserHotelService(uow.users_hotels).assign_user_to_hotel(
            user_id=user_id,
            hotel_id=hotel_id,
            role=UserRole.OWNER,
        )
        await uow.commit()
