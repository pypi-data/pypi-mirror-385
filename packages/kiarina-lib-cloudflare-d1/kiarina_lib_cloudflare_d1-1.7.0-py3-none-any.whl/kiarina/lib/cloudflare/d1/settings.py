from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class D1Settings(BaseSettings):
    database_id: str


settings_manager = SettingsManager(D1Settings, multi=True)
