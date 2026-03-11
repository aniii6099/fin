from math import sqrt

DISTURBANCE_THRESHOLD = 2.5


def detect_disturbance(ax: float, ay: float, az: float) -> dict:
    smv = sqrt((ax ** 2) + (ay ** 2) + (az ** 2))
    return {
        "disturbance_detected": smv > DISTURBANCE_THRESHOLD,
        "smv": round(smv, 4),
    }
