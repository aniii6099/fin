import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Awaitable, Callable

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

import models
from ai.anomaly_detection import detect_anomaly
from ai.contact_watchdog import ContactWatchdog
from ai.fall_detection import detect_disturbance
from ai.risk_scoring import score_risk
from config import settings

logger = logging.getLogger(__name__)
BroadcastFn = Callable[[int, dict], Awaitable[None]]


class MQTTService:
    def __init__(self, session_factory, broadcast_fn: BroadcastFn, loop: asyncio.AbstractEventLoop):
        self.session_factory = session_factory
        self.broadcast_fn = broadcast_fn
        self.loop = loop
        self.stop_event = asyncio.Event()
        self.contact_watchdog = ContactWatchdog(timeout_seconds=120)

        self.last_heartbeat: dict[int, datetime] = {}
        self.offline_alerted: set[int] = set()
        self.state_lock = Lock()

        self.client = mqtt.Client(client_id=settings.mqtt_client_id, protocol=mqtt.MQTTv311)
        if settings.mqtt_username:
            self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    async def run_forever(self):
        self.start()
        try:
            await self.stop_event.wait()
        finally:
            self.stop()

    def start(self):
        self.client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
        self.client.loop_start()
        logger.info("MQTT connecting to %s:%s", settings.mqtt_host, settings.mqtt_port)

    def stop(self):
        self.stop_event.set()
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as exc:
            logger.warning("MQTT stop failed: %s", exc)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe("healtech/vitals/#")
            client.subscribe("healtech/device/#")
            logger.info("MQTT subscribed to vitals and device topics")
        else:
            logger.error("MQTT connection failed: rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning("Unexpected MQTT disconnect (rc=%s)", rc)

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            patient_id = self._resolve_patient_id(payload, message.topic)
            if patient_id is None:
                return

            if message.topic.startswith("healtech/device/"):
                self._handle_device_heartbeat(patient_id)
                return

            merged_payload = self._handle_vitals_message(patient_id, payload)
            if merged_payload:
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_fn(patient_id, merged_payload),
                    self.loop,
                )
        except Exception as exc:
            logger.exception("MQTT message handling failed: %s", exc)

    def _resolve_patient_id(self, payload: dict, topic: str) -> int | None:
        if "patient_id" in payload:
            try:
                return int(payload["patient_id"])
            except (TypeError, ValueError):
                return None

        last = topic.split("/")[-1]
        return int(last) if last.isdigit() else None

    def _handle_device_heartbeat(self, patient_id: int):
        now = datetime.now(timezone.utc)
        with self.state_lock:
            self.last_heartbeat[patient_id] = now
            self.offline_alerted.discard(patient_id)

    def _handle_vitals_message(self, patient_id: int, payload: dict) -> dict | None:
        contact = bool(payload.get("contact", False))
        temp = float(payload.get("temp", 0.0))
        ax = float(payload.get("ax", 0.0))
        ay = float(payload.get("ay", 0.0))
        az = float(payload.get("az", 0.0))
        hr = float(payload.get("hr")) if contact and payload.get("hr") is not None else None
        spo2 = float(payload.get("spo2")) if contact and payload.get("spo2") is not None else None

        db: Session = self.session_factory()
        try:
            patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
            if not patient:
                logger.warning("Unknown patient id=%s received via MQTT", patient_id)
                return None

            now = datetime.utcnow()
            vital = models.PatientVital(
                patient_id=patient_id,
                contact=contact,
                hr=hr,
                spo2=spo2,
                temp=temp,
                ax=ax,
                ay=ay,
                az=az,
                timestamp=now,
            )
            db.add(vital)
            db.flush()

            seconds_since_contact = 0
            if contact:
                self.contact_watchdog.mark_contact(patient_id, datetime.now(timezone.utc))
                seconds_since_contact = 0
            else:
                seconds_since_contact = self.contact_watchdog.evaluate(patient_id)["seconds_since_contact"]

            if not contact:
                db.commit()
                return {
                    "patient_id": patient_id,
                    "status": "AWAITING_READING",
                    "vitals": None,
                    "contact": False,
                    "disturbance": None,
                    "anomaly": None,
                    "risk": None,
                    "alert_type": None,
                    "alert_id": None,
                    "seconds_since_contact": seconds_since_contact,
                }

            disturbance = detect_disturbance(ax=ax, ay=ay, az=az)
            anomaly = detect_anomaly(hr=hr or 0.0, spo2=spo2 or 0.0, temp=temp)
            risk = score_risk(hr=hr or 0.0, spo2=spo2 or 0.0, temp=temp, conditions=patient.conditions)

            alert_type = None
            alert_id = None

            if disturbance["disturbance_detected"]:
                db.add(
                    models.DeviceEvent(
                        patient_id=patient_id,
                        event_type="DISTURBANCE",
                        detail=f"Device disturbance detected with SMV={disturbance['smv']}",
                        timestamp=datetime.utcnow(),
                    )
                )
                alert = models.AIAlert(
                    patient_id=patient_id,
                    alert_type="DISTURBANCE",
                    severity="HIGH",
                    message="Device disturbed near patient",
                    timestamp=datetime.utcnow(),
                    resolved=False,
                )
                db.add(alert)
                db.flush()
                alert_type = "DISTURBANCE"
                alert_id = alert.id
            elif anomaly["anomaly"]:
                severity = "HIGH" if risk["risk_level"] == "HIGH" else "MEDIUM"
                alert = models.AIAlert(
                    patient_id=patient_id,
                    alert_type="ANOMALY",
                    severity=severity,
                    message=anomaly["description"],
                    timestamp=datetime.utcnow(),
                    resolved=False,
                )
                db.add(alert)
                db.flush()
                alert_type = "ANOMALY"
                alert_id = alert.id

            db.commit()

            return {
                "patient_id": patient_id,
                "status": "ACTIVE",
                "vitals": {
                    "hr": hr,
                    "spo2": spo2,
                    "temp": temp,
                    "timestamp": vital.timestamp.isoformat(),
                },
                "contact": True,
                "disturbance": disturbance,
                "anomaly": anomaly,
                "risk": risk,
                "alert_type": alert_type,
                "alert_id": alert_id,
                "seconds_since_contact": seconds_since_contact,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    async def monitor_device_offline(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(30)
            await self._check_device_offline_once()

    async def monitor_contact_timeouts(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(30)
            await self._check_contact_timeouts_once()

    async def _check_device_offline_once(self):
        now = datetime.now(timezone.utc)
        threshold = timedelta(seconds=60)
        with self.state_lock:
            snapshot = dict(self.last_heartbeat)

        for patient_id, last_seen in snapshot.items():
            if now - last_seen <= threshold:
                continue
            with self.state_lock:
                if patient_id in self.offline_alerted:
                    continue
                self.offline_alerted.add(patient_id)

            db: Session = self.session_factory()
            try:
                patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
                if not patient:
                    continue

                event = models.DeviceEvent(
                    patient_id=patient_id,
                    event_type="DEVICE_OFFLINE",
                    detail="No device heartbeat for over 60 seconds",
                    timestamp=datetime.utcnow(),
                )
                alert = models.AIAlert(
                    patient_id=patient_id,
                    alert_type="DEVICE_OFFLINE",
                    severity="HIGH",
                    message="Device offline - check ESP32 connection",
                    timestamp=datetime.utcnow(),
                    resolved=False,
                )
                db.add_all([event, alert])
                db.commit()
                db.refresh(alert)

                payload = {
                    "patient_id": patient_id,
                    "status": "DEVICE_OFFLINE",
                    "vitals": None,
                    "contact": False,
                    "disturbance": None,
                    "anomaly": None,
                    "risk": None,
                    "alert_type": "DEVICE_OFFLINE",
                    "alert_id": alert.id,
                    "seconds_since_contact": self.contact_watchdog.evaluate(patient_id)["seconds_since_contact"],
                }
                await self.broadcast_fn(patient_id, payload)
            except Exception as exc:
                db.rollback()
                logger.exception("Failed to create DEVICE_OFFLINE alert: %s", exc)
            finally:
                db.close()

    async def _check_contact_timeouts_once(self):
        db: Session = self.session_factory()
        try:
            patient_ids = [row[0] for row in db.query(models.Patient.id).all()]
        finally:
            db.close()

        for patient_id in patient_ids:
            should_trigger, seconds = self.contact_watchdog.should_trigger(patient_id)
            if not should_trigger:
                continue

            db = self.session_factory()
            try:
                event = models.DeviceEvent(
                    patient_id=patient_id,
                    event_type="NO_CONTACT_TIMEOUT",
                    detail="No contact=true reading for over 120 seconds",
                    timestamp=datetime.utcnow(),
                )
                alert = models.AIAlert(
                    patient_id=patient_id,
                    alert_type="NO_CONTACT_TIMEOUT",
                    severity="MEDIUM",
                    message="Patient has not used sensor for over 2 minutes",
                    timestamp=datetime.utcnow(),
                    resolved=False,
                )
                db.add_all([event, alert])
                db.commit()
                db.refresh(alert)

                payload = {
                    "patient_id": patient_id,
                    "status": "AWAITING_READING",
                    "vitals": None,
                    "contact": False,
                    "disturbance": None,
                    "anomaly": None,
                    "risk": None,
                    "alert_type": "NO_CONTACT_TIMEOUT",
                    "alert_id": alert.id,
                    "seconds_since_contact": seconds,
                }
                await self.broadcast_fn(patient_id, payload)
            except Exception as exc:
                db.rollback()
                logger.exception("Failed to create NO_CONTACT_TIMEOUT alert: %s", exc)
            finally:
                db.close()
