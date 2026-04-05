from enum import Enum

from pydantic import BaseModel

from auth.application.schemas.roles import SystemRole, UserRole


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenBase(BaseModel):
    sub: str
    exp: int | None = None
    token_type: TokenType


class HotelAccessPayload(BaseModel):
    id: int
    user_role: UserRole


class TokenAccessPayload(TokenBase):
    system_role: SystemRole | None = None
    hotels: list[HotelAccessPayload] | None = None


class TokenRefreshPayload(TokenBase):
    jti: str | None = None


