from __future__ import annotations

from sqlalchemy.orm import Session

from .db import SessionLocal, engine
from .models import Base, User, Dataset, UserDatasetAccess
from .core.security import hash_password
from .core.config import get_settings


def main() -> None:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
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
            db.refresh(admin)
        ds = db.query(Dataset).filter(Dataset.key == 'sample').first()
        if not ds:
            ds = Dataset(key='sample', name='Sample Dataset', description='Seed dataset')
            db.add(ds)
            db.commit()
            db.refresh(ds)
        if not db.query(UserDatasetAccess).filter(UserDatasetAccess.user_id == admin.id, UserDatasetAccess.dataset_id == ds.id).first():
            db.add(UserDatasetAccess(user_id=admin.id, dataset_id=ds.id))
            db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    main()
