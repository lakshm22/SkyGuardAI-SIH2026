# SkyGuard AI — Software-Only Demonstration Plan

SkyGuard is demonstrated as a software AWS network. The simulator produces the same
Temperature/Pressure/Relative-Humidity telemetry contract expected from a physical
ESP32/BME280 gateway and sends it to `POST /api/readings`.

## Recommended 6-minute sequence

1. Start FastAPI and React.
2. Start `python -m simulator.stream` and show normal live telemetry.
3. Run `--scenario isolated_temperature_fault` and select AWS03.
4. Show anomaly score, confidence, SHAP contributions, temporal/spatial evidence,
   diagnosis and AI-assisted corrected value.
5. Run `--scenario regional_event` and show that multiple nearby stations move together,
   reducing the probability of an isolated sensor fault.
6. Run the frozen-sensor scenario and show repeated-value detection.
7. Stop a simulated station or use `/api/telemetry/health` to demonstrate telemetry
   continuity monitoring.
8. Open the evaluation output and explain that its metrics are from controlled injected
   anomalies, not claimed real-world accuracy.

## Physical deployment path

```text
Current demonstration:
Software AWS simulator → FastAPI → SkyGuard AI → React

Deployment-ready path:
BME280 → ESP32 → HTTP/MQTT → FastAPI → SkyGuard AI → React
```

The detector and explanation engine do not need to change when the data source changes.
