from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Talangraga Backend"
    ENV: str = "dev"
    API_PREFIX: str = "/api"

    DATABASE_URL: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
