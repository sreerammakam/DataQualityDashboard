from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .models import DimensionEnum


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Users
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    dataset_ids: List[int] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    dataset_ids: Optional[List[int]] = None


class UserOut(UserBase):
    id: int

    model_config = {
        'from_attributes': True
    }


# Datasets
class DatasetBase(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    is_active: bool = True


class DatasetCreate(DatasetBase):
    pass


class DatasetOut(DatasetBase):
    id: int

    model_config = {
        'from_attributes': True
    }


# Metrics
class MetricRecordBase(BaseModel):
    dataset_id: int
    dimension: DimensionEnum
    metric_name: str
    metric_value: float
    recorded_at: Optional[datetime] = None


class MetricRecordCreate(MetricRecordBase):
    pass


class MetricRecordOut(MetricRecordBase):
    id: int

    model_config = {
        'from_attributes': True
    }


class MetricsSummaryPoint(BaseModel):
    recorded_at: datetime
    value: float


class DimensionSummary(BaseModel):
    dimension: DimensionEnum
    latest_value: Optional[float] = None
    latest_at: Optional[datetime] = None


class TimeseriesResponse(BaseModel):
    metric_name: str
    points: List[MetricsSummaryPoint]
