from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    APP_NAME: str
    DETA_KEY: str
    DETA_ID: str
    NO_REPLY_EMAIL: str
    SENDGRID_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    class Config:
        env_file = ".env"

settings = Settings()
