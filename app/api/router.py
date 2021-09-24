from fastapi import APIRouter

from app.api.endpoints import auth, user, item

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(item.router, prefix="/item", tags=["Item"])
