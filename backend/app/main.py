from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .core.config import get_settings
from .db import engine, get_db
from .models import Base, User, Dataset, UserDatasetAccess
from .core.security import hash_password
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import datasets as datasets_router
from .routers import metrics as metrics_router


settings = get_settings()
app = FastAPI(title="Data Quality Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Create tables
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(datasets_router.router)
app.include_router(metrics_router.router)
