import re

from deta import Base

from jose import jwt, JWTError
from passlib.context import CryptContext

from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.config import settings
from app.models.User import User
from app.models.Token import Token, TokenData
from app.utils.database import get_db, DB


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


def get_current_user(
    db: DB = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
    user = db.users.fetch({"username": token_data.sub})
    if user.count == 1:
        user = User(**user.items[0])

    if user is None:
        raise credentials_exception
    return user


def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_super_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=401, detail="Forbidden")
    return user


def authenticate_user(db: DB, username: str, password: str) -> User:
    fetch = db.users.fetch({"username": username})
    if not fetch.count == 1:
        return False
    user = User(**fetch.items[0])
    if not user.is_verified:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_password(password: str) -> bool:
    """At least 8 characters, containing : one lower case letter, one UPPER case letter, one d1g17, and one $ymbol"""
    return re.match(
        "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", password
    )


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
