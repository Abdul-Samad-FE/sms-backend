"""Common columns mixed into every model.

Mirrors GreenX 2.0 `app/model/base_model.py`. Kept as a mixin (rather than a
shared base class) so each model still inherits from `db.session.Base` and
the metadata stays in one place.
"""

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IdMixin:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
