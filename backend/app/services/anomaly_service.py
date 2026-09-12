from datetime import datetime
import json
from sqlalchemy import desc
from app.database import SessionLocal, Reading, Alert, Station
from app.services.ml_engine import AnomalyEngine
from app.services.advanced_analytics import temporal_score, spatial_analysis, frozen_score, maintenance_forecast
from app.services.explainability import build_explanation
import numpy as np

engine = AnomalyEngine()


def _recent(db, station_id, limit=24):
    return db.query(Reading).filter(Reading.station_id == station_id).order_by(desc(Reading.timestamp)).limit(limit).all()


def corrected(db, station_id, t, p, h):
    recent = [r for r in _recent(db, station_id, 20) if not r.anomaly]
    if not recent:
        return None
    a = np.array([[r.temperature, r.pressure, r.humidity] for r in recent])
    pred = np.median(a, axis=0)
    return {"temperature": round(float(pred[0]), 2), "pressure": round(float(pred[1]), 2), "humidity": round(float(pred[2]), 2)}


def _communication_gap(db, station_id, timestamp, expected_seconds=60):
    previous = db.query(Reading).filter(Reading.station_id == station_id).order_by(desc(Reading.timestamp)).first()
    if not previous:
        return 0.0, None
    gap = max(0.0, (timestamp - previous.timestamp).total_seconds())
    score = float(np.clip((gap - expected_seconds) / max(expected_seconds * 2, 1), 0, 1)) if gap > expected_seconds else 0.0
    return score, gap


def process(reading, source="api", device_id=None):
    db = SessionLocal()
    ts = reading.timestamp or datetime.utcnow()
    try:
        temporal, temporal_peak, baseline = temporal_score(db, reading.station_id, reading.temperature, reading.pressure, reading.humidity, ts)
        spatial_info = spatial_analysis(db, reading.station_id, reading.temperature, reading.pressure, reading.humidity)
        recent = _recent(db, reading.station_id, 12)
        frozen = frozen_score(recent)
        communication, gap_seconds = _communication_gap(db, reading.station_id, ts)

        score, confidence, severity, anomaly, root, components, shap_info = engine.analyze(
            reading.temperature, reading.pressure, reading.humidity,
            temporal=temporal, spatial=spatial_info["score"], frozen=frozen,
            regional_event=spatial_info["regional_event"]
        )

        if communication >= 0.8:
            anomaly = True
            score = max(score, 0.78)
            severity = "Warning" if score < 0.82 else "Critical"
            root = "Communication / telemetry gap"
            confidence = max(confidence, 0.86)
            components["Communication gap"] = communication

        corr = corrected(db, reading.station_id, reading.temperature, reading.pressure, reading.humidity) if anomaly else None
        xai = build_explanation(
            root_cause=root,
            temporal=temporal,
            spatial_info=spatial_info,
            components=components,
            shap_info=shap_info,
            baseline=baseline,
            corrected=corr,
            communication_gap_seconds=gap_seconds,
            frozen=frozen,
        )
        explanation = f"{xai['summary']} {xai['details']}"

        r = Reading(
            station_id=reading.station_id, timestamp=ts,
            temperature=reading.temperature, pressure=reading.pressure, humidity=reading.humidity,
            anomaly=anomaly, score=score, confidence=confidence, severity=severity,
            root_cause=root, explanation=explanation,
            corrected_temperature=corr["temperature"] if corr else None,
            corrected_pressure=corr["pressure"] if corr else None,
            corrected_humidity=corr["humidity"] if corr else None,
            shap_values_json=json.dumps(shap_info),
            xai_json=json.dumps(xai),
            source=source, device_id=device_id,
        )
        db.add(r)
        st = db.query(Station).filter_by(station_id=reading.station_id).first()
        if st:
            st.last_seen = ts
            st.health = float(np.clip(st.health - (score * 4 if anomaly else -0.15), 0, 100))
            st.status = severity
        if anomaly:
            parameter = max([
                ("Temperature", components.get("Temperature jump", 0)),
                ("Pressure", components.get("Pressure deviation", 0)),
                ("Humidity", components.get("Humidity inconsistency", 0)),
                ("Telemetry", components.get("Communication gap", 0)),
            ], key=lambda x: x[1])[0]
            db.add(Alert(
                station_id=reading.station_id, timestamp=ts, parameter=parameter,
                severity=severity, score=score, status="Active", root_cause=root, explanation=explanation
            ))
        db.commit(); db.refresh(r)
        health = st.health if st else 100
        maintenance = maintenance_forecast(db, reading.station_id, health)
        return {
            "station_id": reading.station_id, "timestamp": ts,
            "temperature": reading.temperature, "pressure": reading.pressure, "humidity": reading.humidity,
            "anomaly": anomaly, "anomaly_score": round(score, 3), "confidence": round(confidence, 3),
            "severity": severity, "root_cause": root, "corrected_values": corr,
            "explanation": explanation,
            "feature_contributions": {k: round(float(v), 3) for k, v in components.items()},
            "shap_values": shap_info,
            "xai": xai,
            "temporal_baseline": baseline,
            "spatial_analysis": spatial_info,
            "communication_gap_seconds": round(gap_seconds, 1) if gap_seconds is not None else None,
            "source": source, "device_id": device_id,
            "sensor_health": round(float(health), 1),
            "maintenance_forecast": maintenance,
        }
    finally:
        db.close()
