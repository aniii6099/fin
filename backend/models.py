from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    room_number: Mapped[str] = mapped_column(String(32), nullable=False)
    conditions: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    vitals = relationship("PatientVital", back_populates="patient", cascade="all, delete-orphan")
    device_events = relationship("DeviceEvent", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("AIAlert", back_populates="patient", cascade="all, delete-orphan")


class PatientVital(Base):
    __tablename__ = "patient_vitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    contact: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hr: Mapped[float | None] = mapped_column(Float, nullable=True)
    spo2: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp: Mapped[float] = mapped_column(Float, nullable=False)
    ax: Mapped[float] = mapped_column(Float, nullable=False)
    ay: Mapped[float] = mapped_column(Float, nullable=False)
    az: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    patient = relationship("Patient", back_populates="vitals")


class DeviceEvent(Base):
    __tablename__ = "device_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    detail: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    patient = relationship("Patient", back_populates="device_events")


class AIAlert(Base):
    __tablename__ = "ai_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    patient = relationship("Patient", back_populates="alerts")
