# SkyGuard AI — ESP32 AWS streaming

This folder contains an actual Automatic Weather Station edge gateway for an ESP32 + BME280.

## Data path

```text
BME280
  │
  ├── Temperature (°C)
  ├── Pressure (hPa)
  └── Relative Humidity (%)
          │
          ▼
       ESP32
          │ Wi-Fi / HTTP
          ▼
POST /api/readings
          │
          ▼
SkyGuard AI FastAPI
          │
          ├── ML anomaly detection
          ├── temporal/seasonal baseline
          ├── spatial consistency
          ├── SHAP explanation
          ├── root-cause classification
          └── maintenance/degradation forecast
```

## Hardware

- ESP32 development board
- BME280 breakout
- Jumper wires
- Wi-Fi network reachable by the backend

I2C wiring:

| BME280 | ESP32 |
|---|---|
| VIN/3V3 | 3V3 |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

## Setup

1. Install the Arduino ESP32 board package.
2. Install `Adafruit BME280 Library` and `Adafruit Unified Sensor`.
3. Open `skyguard_esp32_bme280.ino`.
4. Set Wi-Fi credentials and `SKYGUARD_URL` to the backend machine's LAN IP.
5. Ensure Windows/Linux firewall allows TCP port 8000 from the ESP32 LAN.
6. Start FastAPI with `python run.py` or `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
7. Flash the ESP32 and open Serial Monitor at 115200 baud.

The ESP32 sends only the three required meteorological variables plus station/device metadata and timestamp.
