from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from util_common.pydantic_util import show_settings_as_env


class BatchStoreSettings(BaseSettings):
    """Workflow settings class that combines all settings."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
    )

    data_root: Path = Field(
        default=Path("/home/sheldon/repos/docparser_trainer_datasets/data")
    )  # DATA_ROOT 环境变量
    decompress_base_url: str = "http://192.168.8.251:28001"
    unify_base_url: str = "http://192.168.8.251:28002"


batch_store_settings = BatchStoreSettings()

show_settings_as_env(batch_store_settings)
