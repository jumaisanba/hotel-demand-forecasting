from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.user import PasswordUpdate
from auth.application.services import UserService


async def change_password(
        user_id: int,
        passwords_data: PasswordUpdate,
        uow: IUnitOfWork,
) -> None:
    async with uow:
        await UserService(uow.users).change_password(
            user_id=user_id,
            pwd_data=passwords_data
        )
        await uow.commit()
