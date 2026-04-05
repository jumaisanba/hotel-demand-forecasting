from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.principal import HotelAccessPrincipal
from auth.application.schemas.token import TokenRefreshPayload
from auth.application.services.token.jwt_auth import JWTAuthService
from auth.application.use_cases._helpers import get_hotels_payload

from shared.errors import AuthorizationError


async def rotate_tokens(
        refresh_token: str,
        uow: IUnitOfWork,
        auth: JWTAuthService,
) -> tuple[str, str]:
    payload = await auth.read_token(refresh_token)
    if not isinstance(payload, TokenRefreshPayload):
        raise AuthorizationError("Invalid refresh token")

    user_id = int(payload.sub)

    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise AuthorizationError("User not found")

        hotels = await get_hotels_payload(uow=uow, user_id=user_id)

        principal = HotelAccessPrincipal(
            user_id=user_id,
            system_role=user.system_role,
            hotels=hotels,
        )

    access, refresh = await auth.rotate_tokens(
        refresh_payload=payload,
        principal=principal,
    )
    return access, refresh
