from pydantic import BaseModel, Field, ConfigDict

from auth.application.schemas.roles import SystemRole
from auth.application.schemas.token import HotelAccessPayload


class AuthPrincipal(BaseModel):
    user_id: int = Field(..., gt=0)

    model_config = ConfigDict(frozen=True)


class HotelAccessPrincipal(BaseModel):
    user_id: int = Field(..., gt=0)
    system_role: SystemRole
    hotels: list[HotelAccessPayload]

    model_config = ConfigDict(frozen=True)
