import asyncio
import logging
from collections import defaultdict
from contextlib import suppress

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, get_session_factory
from mqtt_client import MQTTService
from routers import alerts, patients, vitals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HealTech Stationary IoT Monitoring API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)
        self.lock = asyncio.Lock()

    async def connect(self, patient_id: int, socket: WebSocket):
        await socket.accept()
        async with self.lock:
            self.connections[patient_id].add(socket)

    async def disconnect(self, patient_id: int, socket: WebSocket):
        async with self.lock:
            if patient_id in self.connections and socket in self.connections[patient_id]:
                self.connections[patient_id].remove(socket)
            if patient_id in self.connections and not self.connections[patient_id]:
                self.connections.pop(patient_id, None)

    async def broadcast(self, patient_id: int, payload: dict):
        async with self.lock:
            sockets = list(self.connections.get(patient_id, set()))

        stale = []
        for socket in sockets:
            try:
                await socket.send_json(payload)
            except Exception:
                stale.append(socket)

        if stale:
            async with self.lock:
                for socket in stale:
                    if patient_id in self.connections and socket in self.connections[patient_id]:
                        self.connections[patient_id].remove(socket)
                if patient_id in self.connections and not self.connections[patient_id]:
                    self.connections.pop(patient_id, None)


manager = ConnectionManager()
app.include_router(patients.router)
app.include_router(vitals.router)
app.include_router(alerts.router)

mqtt_service: MQTTService | None = None
mqtt_task: asyncio.Task | None = None
offline_task: asyncio.Task | None = None
contact_task: asyncio.Task | None = None


@app.on_event("startup")
async def on_startup():
    global mqtt_service, mqtt_task, offline_task, contact_task

    Base.metadata.create_all(bind=engine)

    loop = asyncio.get_running_loop()
    mqtt_service = MQTTService(
        session_factory=get_session_factory(),
        broadcast_fn=manager.broadcast,
        loop=loop,
    )

    mqtt_task = asyncio.create_task(mqtt_service.run_forever())
    offline_task = asyncio.create_task(mqtt_service.monitor_device_offline())
    contact_task = asyncio.create_task(mqtt_service.monitor_contact_timeouts())

    logger.info("Startup complete")


@app.on_event("shutdown")
async def on_shutdown():
    global mqtt_service, mqtt_task, offline_task, contact_task

    if mqtt_service:
        mqtt_service.stop()

    for task in [mqtt_task, offline_task, contact_task]:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task


@app.websocket("/ws/{patient_id}")
async def patient_stream(socket: WebSocket, patient_id: int):
    await manager.connect(patient_id, socket)
    try:
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(patient_id, socket)
    except Exception:
        await manager.disconnect(patient_id, socket)


@app.get("/")
def healthcheck():
    return {"status": "ok"}
