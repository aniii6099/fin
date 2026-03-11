import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from config import settings

load_dotenv()

PATIENT_IDS = [1, 2, 3]


def normal_payload() -> dict:
    return {
        "contact": True,
        "hr": round(random.uniform(68, 96), 2),
        "spo2": round(random.uniform(95, 100), 2),
        "temp": round(random.uniform(36.2, 37.1), 2),
        "ax": round(random.uniform(-0.2, 0.2), 3),
        "ay": round(random.uniform(-1.1, -0.7), 3),
        "az": round(random.uniform(-0.2, 0.2), 3),
    }


def no_contact_payload() -> dict:
    return {
        "contact": False,
        "temp": round(random.uniform(22.5, 26.5), 2),
        "ax": 0.0,
        "ay": 0.0,
        "az": 1.0,
    }


def anomaly_payload() -> dict:
    return {
        "contact": True,
        "hr": 138,
        "spo2": 87,
        "temp": round(random.uniform(37.8, 38.8), 2),
        "ax": round(random.uniform(-0.3, 0.3), 3),
        "ay": round(random.uniform(-1.1, -0.7), 3),
        "az": round(random.uniform(-0.3, 0.3), 3),
    }


def disturbance_payload() -> dict:
    return {
        "contact": True,
        "hr": round(random.uniform(74, 92), 2),
        "spo2": round(random.uniform(95, 99), 2),
        "temp": round(random.uniform(36.3, 37.0), 2),
        "ax": 3.1,
        "ay": 2.8,
        "az": 0.5,
    }


def choose_payload() -> dict:
    r = random.random()
    if r < 0.70:
        return normal_payload()
    if r < 0.90:
        return no_contact_payload()
    if r < 0.97:
        return anomaly_payload()
    return disturbance_payload()


def main():
    client = mqtt.Client(client_id="healtech-mock-stationary")
    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

    client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    client.loop_start()

    last_heartbeat_sent = 0.0
    print("Publishing mock stationary ESP32 data every 2 seconds...")

    try:
        while True:
            now = time.time()
            patient_id = random.choice(PATIENT_IDS)
            vitals = choose_payload()
            vitals["patient_id"] = patient_id
            vitals["timestamp"] = datetime.utcnow().isoformat()
            client.publish(f"healtech/vitals/{patient_id}", json.dumps(vitals), qos=1)

            if now - last_heartbeat_sent >= 10:
                for pid in PATIENT_IDS:
                    heartbeat = {
                        "patient_id": pid,
                        "online": True,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    client.publish(f"healtech/device/{pid}", json.dumps(heartbeat), qos=1)
                last_heartbeat_sent = now

            print(f"[{datetime.utcnow().isoformat()}] patient={patient_id}, payload={vitals}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping publisher")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
