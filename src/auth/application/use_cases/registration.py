from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.user import UserCreate, UserShow
from auth.application.services import UserService


async def register_user(
        uow: IUnitOfWork,
        data: UserCreate
) -> UserShow:
    async with uow:
        user_service = UserService(uow.users)

        user = await user_service.register(data)

        await uow.commit()
        return UserShow.model_validate(user)
