import logging

from fastapi import APIRouter, status

from booking.api.dependencies import UoWDep, CurrentUserIdDep
from booking.api.mappers import map_hotel_create_request_to_dto, map_hotel_dto_to_response
from booking.api.schemas import HotelCreateRequest, HotelResponse
from booking.application.use_cases.create_hotel import create_hotel
from shared.errors import ConflictError, DatabaseError, register_errors, AuthorizationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отель",
    response_description="Созданный отель",
)
@register_errors(
    AuthorizationError,
    ConflictError,
    DatabaseError,
)
async def create_hotel_endpoint(
    request: HotelCreateRequest,
    uow: UoWDep,
    current_user_id: CurrentUserIdDep,
) -> HotelResponse:
    logger.info(
        "Запрос на создание отеля: user_id=%s, name=%s",
        current_user_id,
        request.name,
    )

    data = map_hotel_create_request_to_dto(request)

    result = await create_hotel(
        uow=uow,
        data=data,
        owner_user_id=current_user_id,
    )

    logger.info(
        "Отель успешно создан: hotel_id=%s, owner_user_id=%s",
        result.id,
        current_user_id,
    )

    return map_hotel_dto_to_response(result)