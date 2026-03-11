import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_url: str
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str | None
    mqtt_password: str | None
    mqtt_client_id: str


def _build_db_url() -> str:
    explicit = os.getenv("DB_URL")
    if explicit:
        return explicit

    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "password")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "healtech")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"


settings = Settings(
    db_url=_build_db_url(),
    mqtt_host=os.getenv("MQTT_HOST", "127.0.0.1"),
    mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
    mqtt_username=os.getenv("MQTT_USERNAME") or None,
    mqtt_password=os.getenv("MQTT_PASSWORD") or None,
    mqtt_client_id=os.getenv("MQTT_CLIENT_ID", "healtech-backend"),
)
