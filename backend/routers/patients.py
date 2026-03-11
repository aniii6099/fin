from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(tags=["patients"])


@router.get('/patients', response_model=list[schemas.PatientOut])
def list_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).order_by(models.Patient.id.asc()).all()


@router.post('/patients', response_model=schemas.PatientOut, status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    patient = models.Patient(
        name=payload.name,
        age=payload.age,
        room_number=payload.room_number,
        conditions=payload.conditions,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
