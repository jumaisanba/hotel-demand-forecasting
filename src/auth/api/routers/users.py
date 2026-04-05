from fastapi import APIRouter
from fastapi.openapi.models import Response
from starlette import status

from auth.api.cookies import clear_auth_cookies
from auth.api.dependencies import (
    UoWDep,
    AuthPrincipalDep,
    JWTAuthDep,
)
from auth.application.schemas.user import UserShow, UserCreate, PasswordUpdate
from auth.application.use_cases import (
    change_password,
    register_user,
)
from shared.errors import register_errors, ConflictError, AuthorizationError

router = APIRouter()


@router.post(
    "/register",
    response_model=UserShow,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя в системе",
)
@register_errors(ConflictError)
async def register_user_endpoint(
        data: UserCreate,
        uow: UoWDep,
):
    return await register_user(uow=uow, data=data)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Смена пароля пользователя",
)
@register_errors(AuthorizationError, ConflictError)
async def change_password_endpoint(
        response: Response,
        data: PasswordUpdate,
        principal: AuthPrincipalDep,
        uow: UoWDep,
        auth_service: JWTAuthDep,
):
    await change_password(
        user_id=principal.user_id,
        passwords_data=data,
        uow=uow,
    )
    await auth_service.revoke_all_tokens(user_id=str(principal.user_id))
    clear_auth_cookies(response)
