from pathlib import Path
from pydantic import Field

from shared.base_config import ConfigBase
from shared.db_config import DatabaseConfig


class PredictionConfig(ConfigBase):
    model_dir: Path = Path("/models")

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)


prediction_config = PredictionConfig()
