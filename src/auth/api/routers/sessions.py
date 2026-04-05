from fastapi import APIRouter, Response
from starlette import status

from auth.api.cookies import set_auth_cookies, clear_auth_cookies
from auth.api.dependencies import (
    UoWDep,
    JWTAuthDep,
    AuthPrincipalDep,
    RefreshTokenDep,
)
from auth.application.schemas.user import UserCredentials
from auth.application.use_cases import (
    authenticate,
    rotate_tokens,
    logout,
    logout_all,
)
from shared.errors import register_errors, AuthorizationError

router = APIRouter()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Вход пользователя в систему",
)
@register_errors(AuthorizationError)
async def login_endpoint(
        credentials: UserCredentials,
        response: Response,
        uow: UoWDep,
        auth_service: JWTAuthDep
):
    principal = await authenticate(
        credentials=credentials,
        uow=uow,
    )
    access, refresh = await auth_service.generate_tokens(principal=principal)

    set_auth_cookies(
        response,
        access_token=access,
        refresh_token=refresh,
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Обновление пары access/refresh токенов",
)
@register_errors(AuthorizationError)
async def refresh_endpoint(
        response: Response,
        refresh_token: RefreshTokenDep,
        uow: UoWDep,
        auth_service: JWTAuthDep
):
    access, refresh = await rotate_tokens(
        refresh_token=refresh_token,
        uow=uow,
        auth=auth_service,
    )

    set_auth_cookies(
        response,
        access_token=access,
        refresh_token=refresh,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
)
@register_errors(AuthorizationError)
async def logout_endpoint(
        response: Response,
        refresh_token: RefreshTokenDep,
        auth_service: JWTAuthDep,
):
    await logout(
        refresh_token=refresh_token,
        auth=auth_service,
    )
    clear_auth_cookies(response)


@router.post(
    "/logout/all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход со всех устройств",
)
@register_errors(AuthorizationError)
async def logout_all_endpoint(
        response: Response,
        refresh_token: RefreshTokenDep,
        principal: AuthPrincipalDep,
        auth_service: JWTAuthDep,
):
    await logout_all(
        refresh_token=refresh_token,
        user_id=principal.user_id,
        auth=auth_service,
    )
    clear_auth_cookies(response)
