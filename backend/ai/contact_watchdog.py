from datetime import datetime, timezone


class ContactWatchdog:
    def __init__(self, timeout_seconds: int = 120):
        self.timeout_seconds = timeout_seconds
        self.last_contact_true: dict[int, datetime] = {}
        self.triggered_patients: set[int] = set()

    def mark_contact(self, patient_id: int, when: datetime | None = None):
        timestamp = when or datetime.now(timezone.utc)
        self.last_contact_true[patient_id] = timestamp
        self.triggered_patients.discard(patient_id)

    def evaluate(self, patient_id: int, now: datetime | None = None) -> dict:
        current = now or datetime.now(timezone.utc)
        last = self.last_contact_true.get(patient_id)
        if last is None:
            return {"timeout": False, "seconds_since_contact": 0}

        seconds = int((current - last).total_seconds())
        timeout = seconds > self.timeout_seconds
        return {"timeout": timeout, "seconds_since_contact": max(seconds, 0)}

    def should_trigger(self, patient_id: int, now: datetime | None = None) -> tuple[bool, int]:
        result = self.evaluate(patient_id, now)
        if result["timeout"] and patient_id not in self.triggered_patients:
            self.triggered_patients.add(patient_id)
            return True, result["seconds_since_contact"]
        if not result["timeout"]:
            self.triggered_patients.discard(patient_id)
        return False, result["seconds_since_contact"]
