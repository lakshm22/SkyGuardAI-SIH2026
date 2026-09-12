# Software AWS streaming simulator

This is the software-only demonstration gateway for SkyGuard AI. It emits the
same Temperature/Pressure/Relative Humidity telemetry schema that a physical
ESP32/BME280 gateway would send to `POST /api/readings`.

## Start

From `backend/`:

```bash
python -m simulator.stream
```

## Demonstration scenarios

```bash
python -m simulator.stream --scenario isolated_temperature_fault
python -m simulator.stream --scenario regional_event
python -m simulator.stream --scenario frozen_sensor
python -m simulator.stream --scenario pressure_drift
```

The simulator deliberately uses a telemetry timestamp gap for communication
faults in the API's manual simulation endpoint rather than inventing impossible
sensor values.
