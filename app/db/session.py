"""Database engine, session factory, and the FastAPI session dependency.

The connection string comes from `app.core.config.settings` so the DSN has a
single source of truth across the app, the seeders, and Alembic migrations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# `pool_pre_ping` transparently recycles connections dropped by the DB server
# (common with MySQL's `wait_timeout`), avoiding stale-connection errors.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base shared by every ORM model.
Base = declarative_base()


def get_db():
    """Yield a request-scoped SQLAlchemy session, closing it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
