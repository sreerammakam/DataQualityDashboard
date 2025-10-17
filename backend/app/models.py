from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DimensionEnum(str, enum.Enum):
    completeness = "completeness"
    timeliness = "timeliness"
    validity = "validity"
    accuracy = "accuracy"
    consistency = "consistency"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    dataset_access: Mapped[list["UserDatasetAccess"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    metrics: Mapped[list["MetricRecord"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    user_access: Mapped[list["UserDatasetAccess"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    rules: Mapped[list["QualityRule"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")

class UserDatasetAccess(Base):
    __tablename__ = "user_dataset_access"
    __table_args__ = (UniqueConstraint("user_id", "dataset_id", name="uq_user_dataset"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)

    user: Mapped[User] = relationship(back_populates="dataset_access")
    dataset: Mapped[Dataset] = relationship(back_populates="user_access")


class MetricRecord(Base):
    __tablename__ = "metric_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True, nullable=False)
    dimension: Mapped[DimensionEnum] = mapped_column(Enum(DimensionEnum), index=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="metrics")
class QualityRule(Base):
    __tablename__ = "quality_rules"
    __table_args__ = (UniqueConstraint("dataset_id", "name", name="uq_rule_dataset_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sql_query: Mapped[str] = mapped_column(Text, nullable=False)
    dimension: Mapped[DimensionEnum | None] = mapped_column(Enum(DimensionEnum), nullable=True)
    threshold_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="rules")

Index("ix_metrics_dataset_dimension_time", MetricRecord.dataset_id, MetricRecord.dimension, MetricRecord.recorded_at)
