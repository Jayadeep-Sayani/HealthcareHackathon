import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[str] = mapped_column(String(64), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(32), nullable=False)
    blood_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    insurance_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    primary_language: Mapped[str] = mapped_column(String(64), nullable=False)
    emergency_contact_phone: Mapped[str] = mapped_column(String(64), nullable=False)
    specialist_tag: Mapped[str] = mapped_column(String(255), nullable=False)
    urgency: Mapped[str] = mapped_column(String(64), nullable=False)
    doctor_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    intakes: Mapped[list["SpecialistIntake"]] = relationship(
        back_populates="patient",
        passive_deletes=True,
    )


class SpecialistIntake(Base):
    __tablename__ = "specialist_intakes"

    intake_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
    )
    specialist_tag: Mapped[str] = mapped_column(String(255), nullable=False)
    urgency: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="open")
    notes_log: Mapped[list] = mapped_column(JSON, nullable=False, server_default=text("'[]'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )

    patient: Mapped["Patient"] = relationship(back_populates="intakes")
    handoffs: Mapped[list["Handoff"]] = relationship(
        back_populates="intake",
        passive_deletes=True,
    )


class Handoff(Base):
    __tablename__ = "handoffs"

    handoff_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    intake_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("specialist_intakes.intake_id", ondelete="CASCADE"),
        nullable=False,
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
    )
    specialist_tag: Mapped[str] = mapped_column(String(255), nullable=False)
    urgency: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )

    intake: Mapped["SpecialistIntake"] = relationship(back_populates="handoffs")
