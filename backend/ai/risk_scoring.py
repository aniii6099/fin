def _normalize_conditions(conditions: str) -> set[str]:
    if not conditions:
        return set()
    return {token.strip().lower() for token in conditions.split(',') if token.strip()}


def score_risk(hr: float, spo2: float, temp: float, conditions: str) -> dict:
    reasons = []
    risk = "LOW"

    if spo2 < 90 or hr > 130 or hr < 45:
        risk = "HIGH"
        if spo2 < 90:
            reasons.append("SpO2 below 90")
        if hr > 130:
            reasons.append("Heart rate above 130 bpm")
        if hr < 45:
            reasons.append("Heart rate below 45 bpm")
    elif 90 <= spo2 <= 94 or 100 <= hr <= 130 or temp > 38.0:
        risk = "MEDIUM"
        if 90 <= spo2 <= 94:
            reasons.append("SpO2 in caution range")
        if 100 <= hr <= 130:
            reasons.append("Heart rate elevated")
        if temp > 38.0:
            reasons.append("Temperature above 38 C")
    else:
        reasons.append("Vitals in expected range")

    normalized = _normalize_conditions(conditions)

    if "diabetes" in normalized and risk == "MEDIUM":
        risk = "HIGH"
        reasons.append("Diabetes condition increased risk")

    if "hypertension" in normalized and hr > 110 and risk != "HIGH":
        risk = "HIGH" if risk == "MEDIUM" else "MEDIUM"
        reasons.append("Hypertension with HR above 110 increased risk")

    return {
        "risk_level": risk,
        "reason": "; ".join(reasons),
    }
