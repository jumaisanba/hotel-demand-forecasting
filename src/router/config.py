from pydantic import Field
from pydantic_settings import SettingsConfigDict

from shared.base_config import ConfigBase


class JWTConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str
    hash_algorithm: str = "HS256"


class RouterConfig(ConfigBase):
    jwt_config: JWTConfig = Field(default_factory=JWTConfig)

    auth_url: str = "http://auth:8000"
    booking_url: str = "http://booking:8000"
    prediction_url: str = "http://prediction:8000"
    frontend_url: str = "http://frontend:8080"


router_config = RouterConfig()
