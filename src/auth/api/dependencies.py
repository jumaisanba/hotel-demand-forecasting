import json
from typing import Annotated

from fastapi import Depends, Header, Cookie

from auth.application.ports.token_storage import ITokenStorage
from auth.application.ports.unit_of_work import IUnitOfWork
from auth.application.schemas.principal import AuthPrincipal, HotelAccessPrincipal
from auth.application.schemas.roles import SystemRole
from auth.application.schemas.token import HotelAccessPayload
from auth.application.services import JWTProvider
from auth.application.services.token.jwt_auth import JWTAuthService

from auth.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from auth.infrastructure.redis.token_storage import RedisTokenStorage
from shared.errors import AuthorizationError


def get_uow() -> IUnitOfWork:
    return SQLAlchemyUnitOfWork()


def get_token_provider() -> JWTProvider:
    return JWTProvider()


def get_token_storage() -> ITokenStorage:
    return RedisTokenStorage()


def get_token_auth_service(
        token_provider: JWTProvider = Depends(get_token_provider),
        token_storage: RedisTokenStorage = Depends(get_token_storage)
) -> JWTAuthService:
    return JWTAuthService(
        token_provider=token_provider,
        token_storage=token_storage
    )


def _parse_hotels_header(x_hotels: str) -> list[HotelAccessPayload]:
    try:
        raw_hotels = json.loads(x_hotels)
    except json.JSONDecodeError as exc:
        raise AuthorizationError("Invalid X-Hotels header format") from exc

    if not isinstance(raw_hotels, list):
        raise AuthorizationError("X-Hotels header must be a list")

    try:
        return [HotelAccessPayload(**item) for item in raw_hotels]
    except (TypeError, ValueError) as exc:
        raise AuthorizationError("Invalid X-Hotels header payload") from exc


def get_auth_principal(
        x_user_id: int = Header(..., alias="X-User-Id"),
) -> AuthPrincipal:
    return AuthPrincipal(user_id=x_user_id)


def get_hotel_principal(
        x_user_id: int = Header(..., alias="X-User-Id"),
        x_system_role: SystemRole = Header(..., alias="X-System-Role"),
        x_hotels: str = Header(..., alias="X-Hotels"),
) -> HotelAccessPrincipal:
    hotels = _parse_hotels_header(x_hotels)

    return HotelAccessPrincipal(
        user_id=x_user_id,
        system_role=x_system_role,
        hotels=hotels,
    )


def get_refresh_cookie(
        refresh_token: str | None = Cookie(default=None),
) -> str:
    if not refresh_token:
        raise AuthorizationError("Refresh token missing")
    return refresh_token


UoWDep = Annotated[IUnitOfWork, Depends(get_uow)]
JWTAuthDep = Annotated[JWTAuthService, Depends(get_token_auth_service)]

AuthPrincipalDep = Annotated[AuthPrincipal, Depends(get_auth_principal)]
HotelPrincipalDep = Annotated[HotelAccessPrincipal, Depends(get_hotel_principal)]

RefreshTokenDep = Annotated[str, Depends(get_refresh_cookie)]
