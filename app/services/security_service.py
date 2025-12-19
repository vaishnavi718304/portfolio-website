# app/services/security_service.py
from __future__ import annotations

from typing import List
from sqlalchemy import select

from app.db import db
from app.domain.security import Security


def get_all_securities() -> List[Security]:
    return db.session.scalars(select(Security)).all()
