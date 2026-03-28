"""Ensure per-specialist time slots exist for the patient booking demo."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from database import SessionLocal
from models import AppointmentSlot, Doctor


def ensure_default_appointment_slots() -> None:
    db = SessionLocal()
    try:
        if db.query(AppointmentSlot).first() is not None:
            return
        specialists = db.scalars(select(Doctor).where(Doctor.role == "specialist")).all()
        if not specialists:
            return
        now = datetime.now(timezone.utc)
        slots: list[AppointmentSlot] = []
        for day_offset in range(21):
            day = (now + timedelta(days=day_offset)).date()
            if day.weekday() >= 5:
                continue
            for hour in (9, 10, 11, 13, 14, 15, 16):
                starts_at = datetime(day.year, day.month, day.day, hour, 0, tzinfo=timezone.utc)
                if starts_at <= now:
                    continue
                for spec in specialists:
                    slots.append(AppointmentSlot(doctor_id=spec.id, starts_at=starts_at))
        if slots:
            db.add_all(slots)
            db.commit()
    finally:
        db.close()
