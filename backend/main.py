from datetime import date, datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Pydantic ---


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    age: int
    sex: str
    postal_code: str
    blood_type: str | None = None
    insurance_number: str | None = None
    primary_language: str
    emergency_contact_phone: str
    specialist_tag: str
    urgency: str
    doctor_notes: str = ""


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    age: int | None = None
    sex: str | None = None
    postal_code: str | None = None
    blood_type: str | None = None
    insurance_number: str | None = None
    primary_language: str | None = None
    emergency_contact_phone: str | None = None
    specialist_tag: str | None = None
    urgency: str | None = None
    doctor_notes: str | None = None


class PatientOut(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    age: int
    sex: str
    postal_code: str
    blood_type: str | None
    insurance_number: str | None
    primary_language: str
    emergency_contact_phone: str
    specialist_tag: str
    urgency: str
    doctor_notes: str

    model_config = {"from_attributes": True}


class IntakeCreate(BaseModel):
    patient_id: str
    specialist_tag: str | None = None
    urgency: str | None = None
    status: str = "open"


class IntakeOut(BaseModel):
    intake_id: str
    patient_id: str
    specialist_tag: str
    urgency: str
    status: str
    notes_log: list
    created_at: datetime

    model_config = {"from_attributes": True}


class IntakeUpdate(BaseModel):
    specialist_tag: str | None = None
    urgency: str | None = None
    status: str | None = None
    notes_log: list | None = None


class HandoffCreate(BaseModel):
    intake_id: str
    specialist_tag: str
    urgency: str
    notes: str


class HandoffOut(BaseModel):
    handoff_id: str
    intake_id: str
    patient_id: str
    specialist_tag: str
    urgency: str
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Patients ---


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/patients", response_model=list[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    return db.scalars(select(models.Patient).order_by(models.Patient.last_name, models.Patient.first_name)).all()


@app.post("/api/patients", response_model=PatientOut, status_code=201)
def create_patient(body: PatientCreate, db: Session = Depends(get_db)):
    p = models.Patient(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/api/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.get(models.Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


@app.patch("/api/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: str, body: PatientUpdate, db: Session = Depends(get_db)):
    p = db.get(models.Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p


@app.delete("/api/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.get(models.Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(p)
    db.commit()


# --- Intakes ---


@app.get("/api/intakes/for-specialization/{specialist_tag}", response_model=list[IntakeOut])
def list_intakes_for_specialization(specialist_tag: str, db: Session = Depends(get_db)):
    q = (
        select(models.SpecialistIntake)
        .where(models.SpecialistIntake.specialist_tag == specialist_tag)
        .order_by(models.SpecialistIntake.created_at.desc())
    )
    return db.scalars(q).all()


@app.post("/api/intakes", response_model=IntakeOut, status_code=201)
def create_intake(body: IntakeCreate, db: Session = Depends(get_db)):
    patient = db.get(models.Patient, body.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    tag = body.specialist_tag if body.specialist_tag is not None else patient.specialist_tag
    urg = body.urgency if body.urgency is not None else patient.urgency
    notes_log: list = []
    if patient.doctor_notes.strip():
        notes_log.append(
            {"role": "doctor", "at": _utc_now_iso(), "body": patient.doctor_notes},
        )
    intake = models.SpecialistIntake(
        patient_id=patient.patient_id,
        specialist_tag=tag,
        urgency=urg,
        status=body.status,
        notes_log=notes_log,
    )
    db.add(intake)
    db.commit()
    db.refresh(intake)
    return intake


@app.get("/api/intakes/{intake_id}", response_model=IntakeOut)
def get_intake(intake_id: str, db: Session = Depends(get_db)):
    row = db.get(models.SpecialistIntake, intake_id)
    if not row:
        raise HTTPException(status_code=404, detail="Intake not found")
    return row


@app.patch("/api/intakes/{intake_id}", response_model=IntakeOut)
def update_intake(intake_id: str, body: IntakeUpdate, db: Session = Depends(get_db)):
    row = db.get(models.SpecialistIntake, intake_id)
    if not row:
        raise HTTPException(status_code=404, detail="Intake not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


# --- Handoffs ---


@app.post("/api/handoffs", response_model=HandoffOut, status_code=201)
def create_handoff(body: HandoffCreate, db: Session = Depends(get_db)):
    intake = db.get(models.SpecialistIntake, body.intake_id)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    ho = models.Handoff(
        intake_id=intake.intake_id,
        patient_id=intake.patient_id,
        specialist_tag=body.specialist_tag,
        urgency=body.urgency,
        notes=body.notes,
    )
    log = list(intake.notes_log or [])
    log.append(
        {
            "role": "handoff",
            "at": _utc_now_iso(),
            "to_specialist_tag": body.specialist_tag,
            "urgency": body.urgency,
            "body": body.notes,
        },
    )
    intake.notes_log = log
    intake.specialist_tag = body.specialist_tag
    intake.urgency = body.urgency
    db.add(ho)
    db.commit()
    db.refresh(ho)
    return ho


@app.get("/api/handoffs/{handoff_id}", response_model=HandoffOut)
def get_handoff(handoff_id: str, db: Session = Depends(get_db)):
    row = db.get(models.Handoff, handoff_id)
    if not row:
        raise HTTPException(status_code=404, detail="Handoff not found")
    return row
