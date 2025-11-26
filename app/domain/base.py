# app/domain/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single shared Base for all ORM models."""
    pass
