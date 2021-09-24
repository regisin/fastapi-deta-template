from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException

from app.models.Item import Item, ItemCreate, ItemRead, ItemUpdate, ItemDelete
from app.models.User import User
from app.utils.database import get_db, DB
from app.utils.security import get_super_user

router = APIRouter()


@router.post("/", response_model=ItemRead)
def create_one(
    *, db: DB = Depends(get_db), item: ItemCreate, user: User = Depends(get_super_user)
) -> Any:
    fetch = db.items.fetch({"name": item.name})
    if not fetch.count == 0:
        raise HTTPException(status_code=400, detail="Item already exists")
    return db.items.put(item.dict())


@router.get("/", response_model=List[ItemRead])
def read_all(*, db: DB = Depends(get_db)) -> Any:
    fetch = db.items.fetch()
    return fetch.items


@router.get("/{key}", response_model=ItemRead)
def read_one(*, db: DB = Depends(get_db), key: str) -> Any:
    stored_data = db.items.get(key)
    if not stored_data:
        raise HTTPException(status_code=404, detail="Item not found")
    return stored_data


@router.patch("/patch/{key}", response_model=ItemRead)
def update_one(
    *,
    db: DB = Depends(get_db),
    key: str,
    item: ItemUpdate,
    user: User = Depends(get_super_user)
) -> Any:
    stored_data = db.items.get(key)
    if not stored_data:
        raise HTTPException(status_code=404, detail="Item not found")
    stored_item = Item(**stored_data)
    updated_data = item.dict(exclude_unset=True)
    updated_item = stored_item.copy(update=updated_data)
    return db.items.put(updated_item.dict())


@router.delete("/{key}", response_model=ItemDelete)
def delete_one(
    *, db: DB = Depends(get_db), key: str, user: User = Depends(get_super_user)
) -> Any:
    stored_data = db.items.get(key)
    if not stored_data:
        raise HTTPException(status_code=404, detail="Item not found")
    db.items.delete(key)
    stored_data.pop("key")
    return stored_data
