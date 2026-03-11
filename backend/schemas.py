from datetime import datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=0, le=130)
    room_number: str = Field(min_length=1, max_length=32)
    conditions: str = ""


class PatientOut(PatientCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class VitalOut(BaseModel):
    id: int
    patient_id: int
    contact: bool
    hr: float | None
    spo2: float | None
    temp: float
    ax: float
    ay: float
    az: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    patient_id: int
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool

    model_config = {"from_attributes": True}


class DeviceEventOut(BaseModel):
    id: int
    patient_id: int
    event_type: str
    detail: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class ResolveAlertOut(BaseModel):
    id: int
    resolved: bool
