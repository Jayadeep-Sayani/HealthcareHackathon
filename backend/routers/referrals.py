import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import CareThreadEntry, Doctor, Patient, Referral
from schemas import ReferralAccept, ReferralCreate, ReferralOut

router = APIRouter(prefix="/referrals", tags=["referrals"])

OVERDUE_DAYS = 14
OVERDUE_MIN_URGENCY = 5


@router.post("", response_model=ReferralOut, status_code=201)
def create_referral(body: ReferralCreate, db: Session = Depends(get_db)):
    patient = db.get(Patient, body.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    doctor = db.get(Doctor, body.referring_doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    referral = Referral(
        patient_id=body.patient_id,
        referring_doctor_id=body.referring_doctor_id,
        specialist_type=body.specialist_type,
        urgency=body.urgency,
        clinical_note=body.clinical_note,
        status="pending",
    )
    db.add(referral)
    db.flush()

    entry = CareThreadEntry(
        patient_id=body.patient_id,
        referral_id=referral.id,
        doctor_id=body.referring_doctor_id,
        entry_type="referral_created",
        content=body.clinical_note,
    )
    db.add(entry)
    db.commit()
    db.refresh(referral)

    return _referral_to_out(referral, patient, doctor)


@router.get("", response_model=list[ReferralOut])
def list_referrals(specialty: str | None = None, db: Session = Depends(get_db)):
    query = select(Referral).where(Referral.status == "pending")
    if specialty:
        query = query.where(Referral.specialist_type == specialty)
    query = query.order_by(Referral.urgency.desc(), Referral.created_at.asc())

    referrals = db.scalars(query).all()
    now = datetime.now(timezone.utc)

    result = []
    overdue = []
    normal = []

    for ref in referrals:
        patient = db.get(Patient, ref.patient_id)
        doctor = db.get(Doctor, ref.referring_doctor_id)
        out = _referral_to_out(ref, patient, doctor)

        created = ref.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        days_waiting = (now - created).days
        if ref.urgency >= OVERDUE_MIN_URGENCY and days_waiting > OVERDUE_DAYS:
            out.is_overdue = True
            overdue.append(out)
        else:
            normal.append(out)

    return overdue + normal


@router.post("/{referral_id}/accept", response_model=ReferralOut)
def accept_referral(referral_id: int, body: ReferralAccept, db: Session = Depends(get_db)):
    referral = db.get(Referral, referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    if referral.status == "accepted":
        raise HTTPException(status_code=400, detail="Referral already accepted")

    accepting_doctor = db.get(Doctor, body.doctor_id)
    if not accepting_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    now = datetime.now(timezone.utc)
    referral.status = "accepted"
    referral.accepted_at = now
    referral.accepted_by_doctor_id = body.doctor_id
    referral.booking_token = str(uuid.uuid4())

    entry = CareThreadEntry(
        patient_id=referral.patient_id,
        referral_id=referral.id,
        doctor_id=body.doctor_id,
        entry_type="referral_accepted",
        content=f"Referral accepted by {accepting_doctor.name} ({accepting_doctor.specialty or 'Specialist'}). Patient will be contacted to schedule initial assessment.",
        created_at=now,
    )
    db.add(entry)
    db.commit()
    db.refresh(referral)

    patient = db.get(Patient, referral.patient_id)
    referring_doctor = db.get(Doctor, referral.referring_doctor_id)

    # Trigger email notification (non-blocking)
    try:
        from email_service import send_referral_accepted_email

        if patient and referral.booking_token:
            base = (os.getenv("BOOKING_PUBLIC_BASE_URL") or "http://localhost:5173").rstrip("/")
            booking_url = f"{base}/book/{referral.id}?token={referral.booking_token}"
            send_referral_accepted_email(
                patient_email=patient.email,
                patient_name=patient.name,
                specialist_name=accepting_doctor.name,
                specialty=accepting_doctor.specialty or "Specialist",
                booking_url=booking_url,
            )
    except Exception as e:
        print(f"Email send failed (non-critical): {e}")

    return _referral_to_out(referral, patient, referring_doctor)


def _referral_to_out(
    referral: Referral,
    patient: Patient | None,
    referring_doctor: Doctor | None,
) -> ReferralOut:
    return ReferralOut(
        id=referral.id,
        patient_id=referral.patient_id,
        referring_doctor_id=referral.referring_doctor_id,
        specialist_type=referral.specialist_type,
        urgency=referral.urgency,
        clinical_note=referral.clinical_note,
        status=referral.status,
        created_at=referral.created_at,
        accepted_at=referral.accepted_at,
        accepted_by_doctor_id=referral.accepted_by_doctor_id,
        patient_name=patient.name if patient else None,
        referring_doctor_name=referring_doctor.name if referring_doctor else None,
    )
