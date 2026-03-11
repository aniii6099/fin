from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(tags=["vitals"])


@router.get('/patients/{patient_id}/vitals', response_model=list[schemas.VitalOut])
def get_vitals(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient.id).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    return (
        db.query(models.PatientVital)
        .filter(models.PatientVital.patient_id == patient_id, models.PatientVital.contact.is_(True))
        .order_by(models.PatientVital.timestamp.desc())
        .limit(100)
        .all()
    )


@router.get('/patients/{patient_id}/device-events', response_model=list[schemas.DeviceEventOut])
def get_device_events(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient.id).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    return (
        db.query(models.DeviceEvent)
        .filter(models.DeviceEvent.patient_id == patient_id)
        .order_by(models.DeviceEvent.timestamp.desc())
        .all()
    )
