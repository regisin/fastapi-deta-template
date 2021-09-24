import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordRequestForm

from app.config import settings
from app.models.User import User, UserCreate, UserRead
from app.models.Token import Token
from app.utils.database import get_db, DB
from app.utils.security import (
    validate_password,
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from app.utils.email import send_verification_email

router = APIRouter()


@router.post("/signup", response_model=UserRead, status_code=200)
def user_signup(*, db: DB = Depends(get_db), user: UserCreate):
    """
    Sign up new account:

    - **username**: email address used to verify the account
    - **password**: minimum 8 symbols, must contain at least one lower case letter, one UPPER CASE letter, one numb3r, and one $ymbol
    - **fullname**: full name, not publicly displayed
    """
    # if username exists, return error
    fetch = db.users.fetch({"username": user.username})
    if not fetch.count == 0:
        raise HTTPException(status_code=400, detail="User already exists")
    # if does not exist, check if password is valid
    if not validate_password(user.password):
        raise HTTPException(
            status_code=400, detail="Password does not meet requirements"
        )
    # if valid, add to db and send verification email
    # user.password > to hashed pw > User to db.
    new_user = User(
        username=user.username,
        fullname=user.fullname,
        hashed_password=get_password_hash(user.password),
    )
    new_user = new_user.dict()
    new_user.pop("key")
    new_user = db.users.put(new_user)
    new_user = UserRead(**new_user)

    verification_code = db.verifications.put(new_user.key)["key"]
    send_verification_email(new_user, verification_code)
    return new_user


@router.get("/verify/{key}", status_code=200)
def user_verify(*, db: DB = Depends(get_db), key: str):
    """
    Account verification after signing up:

    - **key**: unique identifier, sent to the email after signing up
    """
    secret_token: str = db.verifications.get(key)
    if not secret_token:
        raise HTTPException(status_code=400, detail="Could not verify user")
    user_key = secret_token["value"]
    user = db.users.get(user_key)
    if not user:
        raise HTTPException(status_code=400, detail="Could not verify user")
    user["is_verified"] = True
    db.users.put(user)
    db.verifications.delete(key)
    return {"detail": "User successfully verified"}


@router.post("/token", response_model=Token)
async def get_access_token(
    *, db: DB = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Obtain a bearer token:

    - **username**: account username, the email used to sign up
    - **password**: account password
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    # print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
