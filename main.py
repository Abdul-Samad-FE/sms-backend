"""Backwards-compatible entry point.

The application factory now lives in `app.main`. Prefer running the server with:

    uvicorn app.main:app --reload

This shim keeps `uvicorn main:app` working for existing tooling.
"""

from app.main import app, create_app  # noqa: F401
