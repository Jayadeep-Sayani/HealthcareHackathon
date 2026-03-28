from datetime import datetime

from pydantic import BaseModel


# --- Auth ---

class LoginRequest(BaseModel):
    username: str


class LoginResponse(BaseModel):
    doctor_id: int
    name: str
    role: str
    specialty: str | None

    model_config = {"from_attributes": True}


# --- Patients ---

class PatientOut(BaseModel):
    id: int
    health_card_id: str
    name: str
    email: str
    date_of_birth: str

    model_config = {"from_attributes": True}


# --- Referrals ---

class ReferralCreate(BaseModel):
    patient_id: int
    referring_doctor_id: int
    specialist_type: str
    urgency: int
    clinical_note: str


class ReferralOut(BaseModel):
    id: int
    patient_id: int
    referring_doctor_id: int
    specialist_type: str
    urgency: int
    clinical_note: str
    status: str
    created_at: datetime
    accepted_at: datetime | None
    accepted_by_doctor_id: int | None
    patient_name: str | None = None
    referring_doctor_name: str | None = None
    is_overdue: bool = False

    model_config = {"from_attributes": True}


class ReferralAccept(BaseModel):
    doctor_id: int


# --- Care Thread ---

class CareThreadEntryOut(BaseModel):
    id: int
    patient_id: int
    referral_id: int | None
    doctor_id: int
    entry_type: str
    content: str
    created_at: datetime
    doctor_name: str | None = None

    model_config = {"from_attributes": True}


# --- AI ---

class TranscriptRequest(BaseModel):
    transcript: str


class TranscriptResponse(BaseModel):
    clinical_summary: str
    suggested_specialist: str
    suggested_urgency: int
    key_symptoms: list[str]


class FinalizeRequest(BaseModel):
    transcript: str
    clinical_note: str
    specialist_type: str
    urgency: int


class FinalizeResponse(BaseModel):
    formal_note: str


# --- Doctors ---

class DoctorOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    specialty: str | None

    model_config = {"from_attributes": True}


# --- Public patient booking (token in email link) ---

class BookingSlotOut(BaseModel):
    id: int
    starts_at: datetime
    booked: bool


class BookingPageResponse(BaseModel):
    patient_name: str
    specialist_name: str
    specialty: str | None
    booked_slot: BookingSlotOut | None
    slots: list[BookingSlotOut]


class BookingClaimRequest(BaseModel):
    token: str
    slot_id: int


class BookingClaimResponse(BaseModel):
    starts_at: datetime
    specialist_name: str
    message: str
