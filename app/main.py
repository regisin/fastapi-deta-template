from fastapi import FastAPI

from app.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=None,
)


app.include_router(api_router, prefix=settings.API_V1_STR)
