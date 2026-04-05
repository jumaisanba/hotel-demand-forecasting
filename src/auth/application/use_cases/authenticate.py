from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.principal import HotelAccessPrincipal
from auth.application.schemas.user import UserCredentials
from auth.application.services import UserService
from auth.application.use_cases._helpers import get_hotels_payload
from shared.errors import AuthorizationError


async def authenticate(
        credentials: UserCredentials,
        uow: IUnitOfWork,
) -> HotelAccessPrincipal:
    async with uow:
        user = await uow.users.get_by_email(str(credentials.email))
        if not user:
            raise AuthorizationError("Invalid credentials")

        UserService(uow.users).verify_credentials(user, credentials.password)

        hotels = await get_hotels_payload(uow, user.id)

        return HotelAccessPrincipal(
            user_id=user.id,
            system_role=user.system_role,
            hotels=hotels,
        )
