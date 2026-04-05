from pydantic import Field
from pydantic_settings import SettingsConfigDict

from shared.base_config import ConfigBase
from shared.db_config import DatabaseConfig


class JWTConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str
    hash_algorithm: str = "HS256"


class RedisConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str
    port: int


class RabbitMQConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")

    host: str
    port: int
    user: str
    password: str
    vhost: str

    @property
    def dsn(self) -> str:
        """DSN для подключения к RabbitMQ."""
        _vhost = self.vhost
        if _vhost.startswith("/"):
            _vhost = _vhost[1:]
        return (
            f"amqp://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{_vhost}"
        )


class AuthConfig(ConfigBase):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    jwt_config: JWTConfig = Field(default_factory=JWTConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)

    password_hash_algorithm: str = "bcrypt"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24


auth_config = AuthConfig()
