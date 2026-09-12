# Real AWS + ESP32 Streaming Guide

SkyGuard AI supports a physical Automatic Weather Station path using an ESP32 and BME280.

## Backend

Run FastAPI so it is reachable from the local network:

```bash
cd backend
python run.py
```

or:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## ESP32

Configure `esp32/skyguard_esp32_bme280.ino` with:

- Wi-Fi SSID/password
- the backend computer's LAN IP
- station ID
- device ID

The board reads:

- Temperature in °C
- Pressure in hPa
- Relative humidity in %

and POSTs JSON to `/api/readings` every 10 seconds.

Example payload:

```json
{
  "station_id": "AWS01",
  "temperature": 31.42,
  "pressure": 1007.81,
  "humidity": 68.20,
  "timestamp": "2026-09-11T15:30:00Z",
  "source": "esp32",
  "device_id": "ESP32-AWS01"
}
```

## Communication fault detection

The backend records the source/device metadata and compares the incoming timestamp with the previous station observation. A sufficiently long telemetry gap is classified as a probable communication/telemetry fault.

## Test without hardware

```bash
curl -X POST http://localhost:8000/api/readings \
  -H "Content-Type: application/json" \
  -d '{"station_id":"AWS01","temperature":31.4,"pressure":1007.8,"humidity":68.2,"source":"aws-gateway","device_id":"TEST-AWS01"}'
```
