from pydantic_settings import BaseSettings
from pydantic import field_validator

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

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()

