from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(tags=["alerts"])


@router.get('/patients/{patient_id}/alerts', response_model=list[schemas.AlertOut])
def get_alerts(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient.id).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    return (
        db.query(models.AIAlert)
        .filter(models.AIAlert.patient_id == patient_id)
        .order_by(models.AIAlert.timestamp.desc())
        .all()
    )


@router.patch('/alerts/{alert_id}/resolve', response_model=schemas.ResolveAlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.AIAlert).filter(models.AIAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')

    alert.resolved = True
    alert.timestamp = alert.timestamp or datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "resolved": alert.resolved}
