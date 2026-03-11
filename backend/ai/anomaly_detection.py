import numpy as np
from sklearn.ensemble import IsolationForest


class VitalsAnomalyDetector:
    def __init__(self):
        rng = np.random.default_rng(42)
        samples = 1200
        hr = rng.uniform(60, 100, samples)
        spo2 = rng.uniform(95, 100, samples)
        temp = rng.uniform(36.1, 37.2, samples)
        training = np.column_stack((hr, spo2, temp))

        self.model = IsolationForest(
            n_estimators=250,
            contamination=0.02,
            random_state=42,
        )
        self.model.fit(training)

    def predict(self, hr: float, spo2: float, temp: float) -> dict:
        sample = np.array([[hr, spo2, temp]], dtype=float)
        anomaly = self.model.predict(sample)[0] == -1
        score = float(self.model.decision_function(sample)[0])

        notes = []
        if hr > 130 or hr < 45:
            notes.append("Heart rate out of safe range")
        if spo2 < 90:
            notes.append("SpO2 critically low")
        elif spo2 < 95:
            notes.append("SpO2 below normal")
        if temp > 38:
            notes.append("Temperature elevated")

        description = "Anomaly detected in vitals" if anomaly else "Vitals pattern appears normal"
        if notes:
            description = f"{description}: {'; '.join(notes)}"

        return {
            "anomaly": anomaly,
            "anomaly_score": round(score, 6),
            "description": description,
        }


detector = VitalsAnomalyDetector()


def detect_anomaly(hr: float, spo2: float, temp: float) -> dict:
    return detector.predict(hr=hr, spo2=spo2, temp=temp)
