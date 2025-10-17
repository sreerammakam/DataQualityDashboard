from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, get_current_admin
from ..models import Dataset, UserDatasetAccess, User
from ..schemas import DatasetCreate, DatasetOut

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("/", response_model=List[DatasetOut])
def list_datasets(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.is_admin:
        return db.query(Dataset).filter(Dataset.is_active == True).all()
    dataset_ids = [a.dataset_id for a in db.query(UserDatasetAccess).filter(UserDatasetAccess.user_id == current.id).all()]
    if not dataset_ids:
        return []
    return db.query(Dataset).filter(Dataset.id.in_(dataset_ids), Dataset.is_active == True).all()


@router.post("/", response_model=DatasetOut)
def create_dataset(payload: DatasetCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    existing = db.query(Dataset).filter(Dataset.key == payload.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dataset key already exists")
    ds = Dataset(key=payload.key, name=payload.name, description=payload.description, is_active=payload.is_active)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds
