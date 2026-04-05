import logging

import httpx
from fastapi import APIRouter, Depends, UploadFile, File, status, Response

from router.api.dependencies import (
    get_http_client,
    get_current_hotel, get_auth_principal
)
from router.api.schemas import (
    BookingImportResponse,
    AccessibleHotel, HotelResponse, HotelCreateRequest, AuthPrincipal
)
from router.api.utils.http import forward_response
from router.api.utils.http import proxy_post
from router.config import router_config
from shared.errors import (
    register_errors,
    AuthorizationError,
    ExternalServiceError,
    DatabaseError,
    MappingError,
    ImportFormatError,
    ConflictError
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/import",
    response_model=BookingImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Импорт бронирований в систему",
)
@register_errors(
    AuthorizationError, MappingError, ImportFormatError,
    ConflictError, DatabaseError, ExternalServiceError
)
async def import_bookings(
        response: Response,
        file: UploadFile = File(...),
        hotel: AccessibleHotel = Depends(get_current_hotel),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Прокси-запрос для загрузки бронирований.
    Отправляет CSV-файл в `booking/booking/import`.
    """

    file_content = await file.read()
    files = {"file": (file.filename, file_content, file.content_type)}

    import_response = await proxy_post(
        client=client,
        url=f"{router_config.booking_url}/booking/import",
        headers={"X-Hotel-Id": str(hotel.id)},
        files=files,
    )
    forward_response(source=import_response, target=response)

    logger.info(
        "Импорт завершён через router_service: hotel_id=%s",
        hotel.id,
    )
    return response


@router.post(
    "/hotels",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отель",
)
@register_errors(
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
)
async def create_hotel(
        response: Response,
        request: HotelCreateRequest,
        principal: AuthPrincipal = Depends(get_auth_principal),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Прокси-запрос на создание отеля.

    Отправляет JSON в сервис booking и пробрасывает
    доверенный идентификатор пользователя в заголовке X-User-Id.
    """
    booking_response = await proxy_post(
        client=client,
        url=f"{router_config.booking_url}/hotel",
        headers={"X-User-Id": str(principal.user_id)},
        json=request.model_dump(),
    )
    forward_response(source=booking_response, target=response)

    logger.info(
        "Создание отеля завершено через router_service: user_id=%s",
        principal.user_id,
    )
    return response
