from typing import Any, List

from pydantic import EmailStr
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from app.models.User import User, UserCreate, UserRead, UserUpdate
from app.utils.database import get_db, DB
from app.utils.security import get_super_user, get_active_user
from app.utils.email import send_verification_email

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_one(
    *,
    db: DB = Depends(get_db),
    new_user: UserCreate,
    user: User = Depends(get_super_user),
) -> Any:
    """
    Create new user.
    """
    fetch = db.users.fetch({"username": new_user.username})
    if not fetch.count == 0:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    verification_code = db.verifications.put(new_user.key)["key"]
    send_verification_email(new_user, verification_code)
    return db.items.put(new_user.dict())


@router.get("/", response_model=List[UserRead])
def read_all(*, db: DB = Depends(get_db), user: User = Depends(get_super_user)) -> Any:
    """
    Retrieve users.
    """
    fetch = db.users.fetch()
    return fetch.items


@router.get("/me", response_model=UserRead)
def read_me(
    db: DB = Depends(get_db),
    current_user: User = Depends(get_active_user),
) -> Any:
    """
    Get current active user.
    """
    return current_user


@router.get("/{key}", response_model=UserRead)
def read_one(
    *, db: DB = Depends(get_db), current_user: User = Depends(get_active_user), key: str
) -> Any:
    """
    Get a specific user by id.
    """
    stored_data = db.users.get(key)
    if not stored_data:
        raise HTTPException(status_code=404, detail="User not found")
    user = User(**stored_data)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Forbidden")
    return user


@router.patch("/patch/me", response_model=UserRead)
def update_me(
    *,
    db: DB = Depends(get_db),
    password: str = Body(None),
    fullname: str = Body(None),
    username: EmailStr = Body(None),
    current_user: User = Depends(get_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = User(**current_user_data)
    if password is not None:
        user_in.password = password
    if fullname is not None:
        user_in.fullname = fullname
    if username is not None:
        user_in.username = username
    user = db.users.put(user_in)
    return user


@router.patch("/patch/{key}", response_model=UserRead)
def update_one(
    *,
    db: DB = Depends(get_db),
    key: str,
    updated_user: UserUpdate,
    user: User = Depends(get_super_user),
) -> Any:
    """
    Update a user.
    """
    stored_data = db.users.get(key)
    if not stored_data:
        raise HTTPException(status_code=404, detail="User not found")
    stored_user = User(**stored_data)
    updated_data = updated_user.dict(exclude_unset=True)
    updated_user = stored_user.copy(update=updated_data)
    return db.users.put(updated_user.dict())


@router.delete("/{key}", response_model=UserRead)
def delete_one(
    *, db: DB = Depends(get_db), key: str, current_user: User = Depends(get_super_user)
) -> Any:
    """
    Update a user.
    """
    stored_data = db.users.get(key)
    if not stored_data:
        raise HTTPException(status_code=404, detail="User not found")
    user = User(**stored_data)
    if user == current_user:
        raise HTTPException(status_code=400, detail="You can't delete yourself")
    db.users.delete(key)
    return user
