# SIH Compliance Matrix

| Requirement | Implementation |
|---|---|
| T/P/RH-only meteorological inputs | `SensorReading` + Isolation Forest features |
| Real-time detection | `POST /api/readings` + continuous monitor |
| Physical AWS streaming | ESP32 + BME280 firmware |
| Sensor spikes | Domain + ML detector |
| Frozen values | Repeated-value detector |
| Communication errors | Telemetry-gap detector |
| Temporal patterns | Historical hour/day-of-year baseline |
| Seasonal patterns | Day-of-year + hour matching baseline |
| Multivariate consistency | Isolation Forest + cross-parameter checks |
| Spatial consistency | Haversine-based nearby-station comparison |
| Genuine regional events | Neighbor consensus classification |
| Confidence | Per-reading confidence score |
| Explainability | Hybrid evidence + SHAP attribution |
| Root cause | Rule/model-based classification |
| Corrected values | Robust median imputation from recent normal readings |
| Sensor health | Health score based on anomaly persistence |
| Degradation prediction | Anomaly-rate + health-trend risk model |
| Maintenance recommendation | Low/Medium/High priority output |
| Dashboard | React/Vite real-time console |
| Anomaly injection | Multiple reproducible scenarios |
| Accuracy evaluation | Synthetic labeled injection benchmark |
| Scalability | FastAPI + SQLAlchemy + PostgreSQL-compatible architecture |
| Edge AI | ESP32 telemetry gateway; backend inference is the current reference deployment |
| Energy efficiency | Lightweight BME280/ESP32 acquisition; no measured energy benchmark claimed |
| Use-case document | `docs/SIH_USE_CASES.md` |
| Example usage | `docs/REAL_AWS_STREAMING.md` + API examples |
