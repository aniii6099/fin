# Stationary ESP32 Real-Time IoT Healthcare Monitoring

## 1) Start Mosquitto Broker

Windows (service install):
```powershell
net start mosquitto
```

Or run foreground broker:
```bash
mosquitto -v
```

## 2) Backend Setup and Run

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
copy .env.example .env   # Linux/macOS: cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 3) Frontend Setup and Run

```bash
cd frontend
npm install
npm run dev
```

## 4) Run Mock ESP32 Publisher

```bash
cd backend
python mock_publisher.py
```

Mock publisher behavior:
- normal contact readings: 70%
- no finger contact: 20%
- anomaly spikes: 7%
- disturbance spikes: 3%
- heartbeat topic publish every 10 seconds
