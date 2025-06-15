from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr


class Settings(BaseSettings):
    # Database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str
    SECRET_KEY: str

    # Redis
    REDIS_URL: str
    REDIS_TTL: int = 3600  

    # Email
    MAIL_USERNAME: EmailStr 
    MAIL_PASSWORD: str 
    MAIL_FROM: EmailStr 
    MAIL_PORT: int 
    MAIL_SERVER: str 
    MAIL_FROM_NAME: str 
    MAIL_STARTTLS: bool 
    MAIL_SSL_TLS: bool 
    USE_CREDENTIALS: bool 
    VALIDATE_CERTS: bool 

    # cloudinary
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str 
    CLOUDINARY_API_SECRET: str 

    @property
    def DB_URL(self):
        """Database URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()