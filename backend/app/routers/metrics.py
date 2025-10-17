from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, ensure_dataset_access
from ..models import MetricRecord, Dataset, User
from ..schemas import MetricRecordCreate, MetricRecordOut, DimensionEnum, DimensionSummary, TimeseriesResponse, MetricsSummaryPoint

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/ingest", response_model=List[MetricRecordOut])
def ingest_metrics(items: List[MetricRecordCreate], current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not items:
        return []
    # Ensure access to all datasets referenced
    dataset_ids = {i.dataset_id for i in items}
    for ds_id in dataset_ids:
        ensure_dataset_access(ds_id, current, db)

    created: List[MetricRecord] = []
    for item in items:
        recorded_at = item.recorded_at or datetime.utcnow()
        rec = MetricRecord(
            dataset_id=item.dataset_id,
            dimension=item.dimension,
            metric_name=item.metric_name,
            metric_value=item.metric_value,
            recorded_at=recorded_at,
        )
        db.add(rec)
        created.append(rec)
    db.commit()
    for rec in created:
        db.refresh(rec)
    return created


@router.get("/latest", response_model=List[DimensionSummary])
def latest_summary(dataset_id: int = Query(...), current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_dataset_access(dataset_id, current, db)

    results: List[DimensionSummary] = []
    for dim in DimensionEnum:
        # latest timestamp per dimension
        latest_ts = (
            db.query(func.max(MetricRecord.recorded_at))
            .filter(MetricRecord.dataset_id == dataset_id, MetricRecord.dimension == dim)
            .scalar()
        )
        if latest_ts is None:
            results.append(DimensionSummary(dimension=dim, latest_value=None, latest_at=None))
            continue
        avg_value = (
            db.query(func.avg(MetricRecord.metric_value))
            .filter(
                MetricRecord.dataset_id == dataset_id,
                MetricRecord.dimension == dim,
                MetricRecord.recorded_at == latest_ts,
            )
            .scalar()
        )
        results.append(DimensionSummary(dimension=dim, latest_value=float(avg_value) if avg_value is not None else None, latest_at=latest_ts))
    return results


@router.get("/timeseries", response_model=List[TimeseriesResponse])
def timeseries(
    dataset_id: int = Query(...),
    dimension: Optional[DimensionEnum] = Query(None),
    metric_name: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_dataset_access(dataset_id, current, db)

    q = db.query(MetricRecord).filter(MetricRecord.dataset_id == dataset_id)
    if dimension is not None:
        q = q.filter(MetricRecord.dimension == dimension)
    if metric_name is not None:
        q = q.filter(MetricRecord.metric_name == metric_name)
    if start is not None:
        q = q.filter(MetricRecord.recorded_at >= start)
    if end is not None:
        q = q.filter(MetricRecord.recorded_at <= end)

    q = q.order_by(MetricRecord.metric_name, MetricRecord.recorded_at)

    series: Dict[str, List[MetricsSummaryPoint]] = defaultdict(list)
    for rec in q.all():
        series[rec.metric_name].append(MetricsSummaryPoint(recorded_at=rec.recorded_at, value=rec.metric_value))

    return [TimeseriesResponse(metric_name=name, points=points) for name, points in series.items()]
