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
    # Seed initial admin and a sample dataset if not present
    from sqlalchemy.orm import Session
    from .db import SessionLocal

    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.INITIAL_ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                full_name="Administrator",
                hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
        # Ensure at least one dataset exists
        ds = db.execute("SELECT id FROM datasets LIMIT 1").fetchone()
        if ds is None:
            dataset = Dataset(key="sample", name="Sample Dataset", description="Seed dataset")
            db.add(dataset)
            db.commit()
            # Grant admin access explicitly (not required since admin bypasses, but tidy)
            db.refresh(dataset)
            db.refresh(admin)
            db.add(UserDatasetAccess(user_id=admin.id, dataset_id=dataset.id))
            db.commit()
    finally:
        db.close()


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(datasets_router.router)
app.include_router(metrics_router.router)
