from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Talangraga Backend"
    ENV: str = "dev"
    API_PREFIX: str = "/api"

    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
