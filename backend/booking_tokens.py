"""Assign booking_token to accepted referrals that pre-date the booking feature."""

import uuid

from sqlalchemy import select

from database import SessionLocal
from models import Referral


def backfill_booking_tokens() -> None:
    db = SessionLocal()
    try:
        refs = db.scalars(
            select(Referral).where(
                Referral.status == "accepted",
                Referral.booking_token.is_(None),
            )
        ).all()
        for r in refs:
            r.booking_token = str(uuid.uuid4())
        if refs:
            db.commit()
    finally:
        db.close()
