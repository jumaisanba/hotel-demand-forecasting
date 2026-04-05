from pydantic import Field, AnyUrl
from pydantic_settings import SettingsConfigDict

from shared.base_config import ConfigBase
from shared.db_config import DatabaseConfig


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


class BookingConfig(ConfigBase):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)
    outbox_publish_interval_sec: float
    outbox_batch_size: int

    auth_url: AnyUrl = Field(default="http://auth:8000")
    auth_timeout_sec: float = Field(default=5.0)


booking_config = BookingConfig()