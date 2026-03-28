from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import AppointmentSlot, CareThreadEntry, Doctor, Patient, Referral
from schemas import BookingClaimRequest, BookingClaimResponse, BookingPageResponse, BookingSlotOut

router = APIRouter(prefix="/public/booking", tags=["public-booking"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _naive_utc_for_sql(dt: datetime | None = None) -> datetime:
    """SQLite stores slot times as naive UTC; SQL comparisons must use naive UTC."""
    base = dt or _utc_now()
    if base.tzinfo is None:
        return base
    return base.replace(tzinfo=None)


def _as_utc(dt: datetime) -> datetime:
    """API responses use timezone-aware UTC (SQLite returns naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _load_referral(referral_id: int, token: str, db: Session) -> Referral:
    referral = db.get(Referral, referral_id)
    if (
        not referral
        or not referral.booking_token
        or referral.booking_token != token
        or referral.status != "accepted"
        or not referral.accepted_by_doctor_id
    ):
        raise HTTPException(status_code=404, detail="Invalid or expired booking link")
    return referral


@router.get("/{referral_id}", response_model=BookingPageResponse)
def get_booking_page(referral_id: int, token: str, db: Session = Depends(get_db)):
    referral = _load_referral(referral_id, token, db)
    patient = db.get(Patient, referral.patient_id)
    specialist = db.get(Doctor, referral.accepted_by_doctor_id)
    if not patient or not specialist:
        raise HTTPException(status_code=404, detail="Invalid booking link")

    naive_cutoff = _naive_utc_for_sql()
    existing = db.scalars(
        select(AppointmentSlot).where(AppointmentSlot.referral_id == referral.id)
    ).first()

    q = (
        select(AppointmentSlot)
        .where(
            AppointmentSlot.doctor_id == specialist.id,
            AppointmentSlot.starts_at > naive_cutoff,
        )
        .order_by(AppointmentSlot.starts_at)
    )
    rows = db.scalars(q).all()

    slots_out: list[BookingSlotOut] = []
    for s in rows:
        slots_out.append(
            BookingSlotOut(
                id=s.id,
                starts_at=_as_utc(s.starts_at),
                booked=s.referral_id is not None,
            )
        )

    booked = None
    if existing:
        booked = BookingSlotOut(
            id=existing.id,
            starts_at=_as_utc(existing.starts_at),
            booked=True,
        )

    return BookingPageResponse(
        patient_name=patient.name,
        specialist_name=specialist.name,
        specialty=specialist.specialty,
        booked_slot=booked,
        slots=slots_out,
    )


@router.post("/{referral_id}/claim", response_model=BookingClaimResponse)
def claim_slot(referral_id: int, body: BookingClaimRequest, db: Session = Depends(get_db)):
    referral = _load_referral(referral_id, body.token, db)

    taken = db.scalars(
        select(AppointmentSlot).where(AppointmentSlot.referral_id == referral.id)
    ).first()
    if taken:
        raise HTTPException(status_code=400, detail="You already have an appointment booked for this referral")

    slot = db.get(AppointmentSlot, body.slot_id)
    if not slot or slot.doctor_id != referral.accepted_by_doctor_id:
        raise HTTPException(status_code=400, detail="Invalid time slot")

    naive_now = _naive_utc_for_sql()
    if slot.starts_at <= naive_now:
        raise HTTPException(status_code=400, detail="That time is no longer available")

    if slot.referral_id is not None:
        raise HTTPException(status_code=409, detail="That time was just booked by someone else")

    slot.referral_id = referral.id
    specialist = db.get(Doctor, referral.accepted_by_doctor_id)
    spec_name = specialist.name if specialist else "your specialist"
    slot_utc = _as_utc(slot.starts_at)
    when = slot_utc.strftime("%A, %b %d at %H:%M UTC")
    entry = CareThreadEntry(
        patient_id=referral.patient_id,
        referral_id=referral.id,
        doctor_id=referral.accepted_by_doctor_id,
        entry_type="note",
        content=f"Patient self-scheduled initial visit with {spec_name} for {when}.",
    )
    db.add(entry)
    db.commit()

    return BookingClaimResponse(
        starts_at=slot_utc,
        specialist_name=spec_name,
        message=f"Your appointment is confirmed for {when}.",
    )
