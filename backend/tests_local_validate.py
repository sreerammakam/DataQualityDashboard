from __future__ import annotations

import os
from typing import List

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./local_test.db")
os.environ.setdefault("JWT_SECRET_KEY", "testsecret")

from fastapi.testclient import TestClient  # type: ignore

from app.main import app
from app.models import Base
from app.db import engine
from app.seed_db import main as seed_main

Base.metadata.create_all(bind=engine)
seed_main()
client = TestClient(app)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_flow():
    # login with seeded admin
    r = client.post("/auth/login", json={"email": "admin@example.com", "password": "admin123"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    # list datasets (seeded)
    r = client.get("/datasets", headers=auth_headers(token))
    assert r.status_code == 200
    datasets = r.json()
    assert len(datasets) >= 1
    dataset_id = datasets[0]["id"]

    # ingest metrics
    payload: List[dict] = [
        {"dataset_id": dataset_id, "dimension": "completeness", "metric_name": "rows_with_nulls_ratio", "metric_value": 0.02},
        {"dataset_id": dataset_id, "dimension": "timeliness", "metric_name": "delay_days", "metric_value": 0.9},
        {"dataset_id": dataset_id, "dimension": "validity", "metric_name": "invalid_values_ratio", "metric_value": 0.01},
        {"dataset_id": dataset_id, "dimension": "accuracy", "metric_name": "match_ratio", "metric_value": 0.97},
        {"dataset_id": dataset_id, "dimension": "consistency", "metric_name": "cross_table_conflicts_ratio", "metric_value": 0.005},
    ]
    r = client.post("/metrics/ingest", headers=auth_headers(token), json=payload)
    assert r.status_code == 200, r.text

    # latest summary
    r = client.get("/metrics/latest", headers=auth_headers(token), params={"dataset_id": dataset_id})
    assert r.status_code == 200, r.text
    latest = r.json()
    assert any(x["latest_value"] is not None for x in latest)

    # timeseries
    r = client.get("/metrics/timeseries", headers=auth_headers(token), params={"dataset_id": dataset_id})
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # create user with dataset access
    r = client.post(
        "/users",
        headers=auth_headers(token),
        json={
            "email": "user1@example.com",
            "full_name": "User One",
            "password": "password123",
            "dataset_ids": [dataset_id],
            "is_admin": False,
            "is_active": True,
        },
    )
    assert r.status_code == 200, r.text


if __name__ == "__main__":
    test_flow()
    print("Local validation passed.")
