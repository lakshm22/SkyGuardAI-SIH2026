# SkyGuard AI — Use Cases

## 1. Weather forecasting quality control

SkyGuard screens incoming AWS observations before they are consumed by forecasting pipelines. A suspicious temperature, pressure or humidity value can be flagged and an estimated corrected value can be supplied for downstream processing.

## 2. Sensor fault detection

The hybrid detector identifies spikes, persistent/frozen values, physically inconsistent combinations and localized deviations. Root-cause labels distinguish likely temperature, pressure, humidity and telemetry problems.

## 3. Genuine regional weather event detection

Nearby AWS stations are compared using geographic distance. If many nearby stations move in the same direction, the system can classify the observation as a probable regional meteorological event instead of treating every station as a sensor failure.

## 4. Agriculture

Reliable temperature, humidity and pressure telemetry supports irrigation decisions, crop-stress monitoring, disease-risk models and microclimate analysis. SkyGuard can flag unreliable observations before they influence these decisions.

## 5. Disaster management

Sudden atmospheric changes can be monitored across a station network. Spatial consensus helps operators distinguish a regional event from an isolated faulty sensor and prioritize alerts.

## 6. Aviation and remote weather monitoring

AWS networks at airports and remote locations can use automated anomaly screening to identify faulty or stale telemetry and reduce the chance of unreliable observations reaching operational systems.

## 7. Preventive sensor maintenance

The maintenance module estimates degradation risk from current sensor health, anomaly persistence and recent anomaly rate. A high-risk station receives an inspection/calibration recommendation.

## 8. Edge/IoT deployment

An ESP32 + BME280 can collect the three required meteorological parameters and stream them over Wi-Fi to the FastAPI ingestion endpoint. This provides a practical path from physical sensor to AI decision layer.

## Example end-to-end scenario

```text
BME280 → ESP32 → Wi-Fi → /api/readings
                         ↓
                 Hybrid AI engine
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
 Temporal/seasonal   Spatial consensus   Isolation Forest
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ↓
             Severity + confidence
                         ↓
        Root cause + SHAP explanation
                         ↓
      Corrected value + maintenance risk
                         ↓
                  Operator dashboard
```
