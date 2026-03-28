"""Lightweight SQLite column adds (create_all does not migrate existing tables)."""

from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_referral_booking_token_column(engine: Engine) -> None:
    if not str(engine.url).startswith("sqlite"):
        return
    with engine.begin() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(referrals)"))]
        if cols and "booking_token" not in cols:
            conn.execute(text("ALTER TABLE referrals ADD COLUMN booking_token VARCHAR(36)"))
