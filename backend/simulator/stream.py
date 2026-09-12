"""Generate realistic multi-station AWS telemetry and POST it to SkyGuard.

Usage:
  python -m simulator.stream --url http://localhost:8000/api/readings
  python -m simulator.stream --scenario isolated_temperature_fault
  python -m simulator.stream --scenario regional_event --interval 2
"""
from __future__ import annotations
import argparse, json, math, random, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

STATIONS = {
    "AWS01": (13.0827, 80.2707),
    "AWS02": (11.0168, 76.9558),
    "AWS03": (9.9252, 78.1198),
    "AWS04": (10.7905, 78.7047),
    "AWS05": (11.4102, 76.6950),
    "AWS06": (9.2885, 79.3129),
}


def normal_reading(station_id: str, tick: int):
    phase = tick / 8.0
    station_offset = (hash(station_id) % 7) * 0.25
    temperature = 30.5 + station_offset + 1.8 * math.sin(phase)
    pressure = 1008.0 - 1.4 * math.sin(phase) + random.gauss(0, 0.35)
    humidity = 72.0 - 5.5 * math.sin(phase) + random.gauss(0, 0.8)
    return {"station_id": station_id, "temperature": round(temperature, 2), "pressure": round(pressure, 2), "humidity": round(max(15, min(98, humidity)), 2)}


def apply_scenario(reading, scenario, tick):
    r = dict(reading)
    if scenario == "isolated_temperature_fault" and r["station_id"] == "AWS03":
        r["temperature"] = 55.0
    elif scenario == "isolated_humidity_fault" and r["station_id"] == "AWS03":
        r["humidity"] = 2.0
    elif scenario == "pressure_drift" and r["station_id"] == "AWS04":
        r["pressure"] = 955.0
    elif scenario == "regional_event":
        r["temperature"] += 11.0
        r["humidity"] = min(98.0, r["humidity"] + 8.0)
    elif scenario == "frozen_sensor" and r["station_id"] == "AWS02":
        r["temperature"], r["pressure"], r["humidity"] = 31.4, 1007.2, 71.0
    return r


def post(url, payload):
    body = json.dumps(payload).encode()
    req = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def main():
    parser = argparse.ArgumentParser(description="SkyGuard software AWS telemetry stream")
    parser.add_argument("--url", default="http://localhost:8000/api/readings")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--scenario", choices=["normal", "isolated_temperature_fault", "isolated_humidity_fault", "pressure_drift", "regional_event", "frozen_sensor", "communication_gap"], default="normal")
    args = parser.parse_args()
    tick = 0
    print(f"SkyGuard AWS simulator → {args.url}")
    print(f"Scenario: {args.scenario}; interval: {args.interval}s")
    while True:
        tick += 1
        for station_id in STATIONS:
            if args.scenario == 'communication_gap' and station_id == 'AWS06':
                print('AWS06: telemetry intentionally withheld (communication-gap demo)')
                continue
            reading = apply_scenario(normal_reading(station_id, tick), args.scenario, tick)
            payload = {
                **reading,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "software-aws-simulator",
                "device_id": f"SIM-{station_id}",
            }
            try:
                result = post(args.url, payload)
                marker = "ANOMALY" if result.get("anomaly") else "normal"
                print(f"{station_id}: {marker:7} T={reading['temperature']:5.1f} P={reading['pressure']:7.1f} RH={reading['humidity']:5.1f} | {result.get('root_cause','')}")
            except Exception as exc:
                print(f"{station_id}: stream error: {exc}")
        time.sleep(max(0.5, args.interval))


if __name__ == "__main__":
    main()
