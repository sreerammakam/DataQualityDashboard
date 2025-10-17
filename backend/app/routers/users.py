from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_admin
from ..core.security import hash_password
from ..models import User, Dataset, UserDatasetAccess
from ..schemas import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=payload.is_active,
        is_admin=payload.is_admin,
    )
    db.add(user)
    db.flush()

    if payload.dataset_ids:
        datasets = db.query(Dataset).filter(Dataset.id.in_(payload.dataset_ids)).all()
        for ds in datasets:
            db.add(UserDatasetAccess(user_id=user.id, dataset_id=ds.id))

    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(User).all()


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin
    if payload.dataset_ids is not None:
        # reset access
        db.query(UserDatasetAccess).filter(UserDatasetAccess.user_id == user.id).delete()
        if payload.dataset_ids:
            datasets = db.query(Dataset).filter(Dataset.id.in_(payload.dataset_ids)).all()
            for ds in datasets:
                db.add(UserDatasetAccess(user_id=user.id, dataset_id=ds.id))

    db.commit()
    db.refresh(user)
    return user
