"""SMS backend application factory.

Builds the FastAPI app, mounts the versioned v1 router under `/api/v1`, and uses
a lifespan handler to run idempotent seeders on startup. `create_all` is kept as
a development fallback for environments where Alembic migrations haven't been
applied yet; in production `alembic upgrade head` creates the schema instead.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import api_router as v1_router
from app.core.config import settings
from app.db.session import Base, engine
import app.models  # noqa: F401 — register every model on Base.metadata
from app.seeds.runner import run_all_seeds

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup/shutdown hook (replaces the deprecated `on_event` handlers)."""
    # Dev fallback: ensure tables exist when Alembic hasn't been run yet. This
    # is a no-op once `alembic upgrade head` has created everything.
    Base.metadata.create_all(bind=engine)
    try:
        run_all_seeds()
    except Exception as exc:  # never let seeding crash the app
        logger.exception("Seeding failed: %s", exc)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    application.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    @application.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.ENV,
        }

    return application


app = create_app()
