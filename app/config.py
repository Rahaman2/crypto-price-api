from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Crypto Price API"
    debug: bool = False

    # External API URLs
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    fear_greed_url: str = "https://api.alternative.me/fng/"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
