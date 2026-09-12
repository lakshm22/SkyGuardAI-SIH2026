"""Temporal, spatial and maintenance analytics for SkyGuard AI."""
from __future__ import annotations

from datetime import datetime, timedelta
import math
import numpy as np

from app.database import Reading, Station

FEATURES = ("temperature", "pressure", "humidity")
SCALE = np.array([5.0, 5.0, 15.0])


def _arr(rows):
    return np.array([[r.temperature, r.pressure, r.humidity] for r in rows], dtype=float)


def seasonal_baseline(db, station_id: str, timestamp: datetime, min_samples: int = 8):
    """Estimate expected T/P/RH using historical hour-of-day + day-of-year buckets.

    Falls back to recent station history when a seasonal bucket has too few samples.
    This is intentionally lightweight so it can run at the edge/backend without a
    heavyweight forecasting model.
    """
    rows = (
        db.query(Reading)
        .filter(Reading.station_id == station_id, Reading.anomaly == False)  # noqa: E712
        .order_by(Reading.timestamp.desc())
        .limit(2000)
        .all()
    )
    if not rows:
        return None

    # Prefer readings close to the same hour and day-of-year. The tolerances widen
    # automatically when historical data is sparse.
    doy = timestamp.timetuple().tm_yday
    hour = timestamp.hour
    scored = []
    for r in rows:
        rdoy = r.timestamp.timetuple().tm_yday
        hour_diff = min(abs(r.timestamp.hour - hour), 24 - abs(r.timestamp.hour - hour))
        doy_diff = min(abs(rdoy - doy), 365 - abs(rdoy - doy))
        score = hour_diff / 6.0 + doy_diff / 45.0
        scored.append((score, r))
    scored.sort(key=lambda x: x[0])
    selected = [r for score, r in scored if score <= 3.0][:120]
    if len(selected) < min_samples:
        selected = rows[: min(120, len(rows))]
    a = _arr(selected)
    return {
        "temperature": float(np.median(a[:, 0])),
        "pressure": float(np.median(a[:, 1])),
        "humidity": float(np.median(a[:, 2])),
        "sample_count": len(selected),
    }


def temporal_score(db, station_id, t, p, h, timestamp):
    baseline = seasonal_baseline(db, station_id, timestamp)
    if not baseline:
        return 0.0, 0.0, None
    current = np.array([t, p, h], dtype=float)
    expected = np.array([baseline[k] for k in FEATURES])
    residual = np.abs(current - expected) / SCALE
    score = float(np.clip(np.mean(residual) / 2.0, 0, 1))
    # A high score means the current reading is far from its learned temporal baseline.
    return score, float(np.max(residual.clip(0, 1))), baseline


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def spatial_analysis(db, station_id, t, p, h, radius_km=250):
    """Compare a station with geographically nearby stations.

    Two signals are kept separate:
    - spatial mismatch: difference from the nearby regional median;
    - regional consensus: whether nearby stations are also abnormal relative to
      their own historical baselines. This prevents a coherent regional event
      from disappearing simply because the regional median moved with it.
    """
    station = db.query(Station).filter_by(station_id=station_id).first()
    if not station:
        return {"score": 0.0, "neighbor_count": 0, "regional_event": False, "isolated": False}

    stations = db.query(Station).all()
    vals = []
    for other in stations:
        if other.station_id == station_id:
            continue
        distance = haversine_km(station.latitude, station.longitude, other.latitude, other.longitude)
        if distance > radius_km:
            continue
        r = db.query(Reading).filter(Reading.station_id == other.station_id).order_by(Reading.timestamp.desc()).first()
        if r:
            vals.append((distance, r))

    if not vals:
        return {"score": 0.0, "neighbor_count": 0, "regional_event": False, "isolated": False}

    arr = np.array([[r.temperature, r.pressure, r.humidity] for _, r in vals], dtype=float)
    current = np.array([t, p, h], dtype=float)
    med = np.median(arr, axis=0)
    deviations = np.abs(current - med) / SCALE
    score = float(np.clip(np.mean(deviations) / 2.0, 0, 1))
    current_station_anomaly = bool(np.mean(deviations) > 0.65)

    # Determine whether the current station and neighboring stations themselves
    # show a deviation from their own historical baselines.
    current_history = (
        db.query(Reading)
        .filter(Reading.station_id == station_id, Reading.anomaly == False)  # noqa: E712
        .order_by(Reading.timestamp.desc())
        .limit(24)
        .all()
    )
    if len(current_history) >= 4:
        current_hist = np.array([[x.temperature, x.pressure, x.humidity] for x in current_history], dtype=float)
        current_baseline = np.median(current_hist, axis=0)
        current_residual = np.abs(current - current_baseline) / SCALE
        current_station_anomaly = bool(np.mean(current_residual) > 0.65)

    # Determine whether neighboring stations themselves show a deviation from
    # their own recent normal baselines. This is the regional-event signal.
    neighbor_anomalies = 0
    directional_matches = 0
    if len(current_history) >= 4:
        current_direction = np.sign(current - current_baseline)
    else:
        current_direction = np.sign(current - med)
    for _, neighbor in vals:
        history = (
            db.query(Reading)
            .filter(Reading.station_id == neighbor.station_id, Reading.anomaly == False)  # noqa: E712
            .order_by(Reading.timestamp.desc())
            .limit(24)
            .all()
        )
        if len(history) < 4:
            continue
        hist = np.array([[x.temperature, x.pressure, x.humidity] for x in history], dtype=float)
        baseline = np.median(hist, axis=0)
        residual = np.abs(np.array([neighbor.temperature, neighbor.pressure, neighbor.humidity]) - baseline) / SCALE
        if float(np.mean(residual)) > 0.65:
            neighbor_anomalies += 1
            direction = np.sign(np.array([neighbor.temperature, neighbor.pressure, neighbor.humidity]) - baseline)
            if np.sum(direction == current_direction) >= 2:
                directional_matches += 1

    eligible = max(1, len(vals))
    consensus_ratio = neighbor_anomalies / eligible
    regional_event = current_station_anomaly and consensus_ratio >= 0.50 and directional_matches >= max(1, int(eligible * 0.5))
    isolated = current_station_anomaly and not regional_event

    return {
        "score": score,
        "neighbor_count": len(vals),
        "regional_event": bool(regional_event),
        "isolated": bool(isolated),
        "regional_consensus_ratio": round(float(consensus_ratio), 3),
        "regional_direction_matches": directional_matches,
        "regional_median": {k: round(float(v), 2) for k, v in zip(FEATURES, med)},
        "radius_km": radius_km,
    }


def frozen_score(rows):
    if len(rows) < 5:
        return 0.0
    recent = _arr(rows[:8])
    unique = len({tuple(np.round(x, 4)) for x in recent})
    return 1.0 if unique <= 1 else max(0.0, 1.0 - unique / len(recent))


def maintenance_forecast(db, station_id, current_health):
    rows = (
        db.query(Reading)
        .filter(Reading.station_id == station_id)
        .order_by(Reading.timestamp.desc())
        .limit(120)
        .all()
    )
    if not rows:
        return {"degradation_risk": 0.0, "maintenance_priority": "Low", "recommendation": "Insufficient telemetry"}

    anomalies = sum(bool(r.anomaly) for r in rows)
    anomaly_rate = anomalies / len(rows)
    recent_anomalies = sum(bool(r.anomaly) for r in rows[:24]) / min(24, len(rows))
    # Health trend proxy: compare the current health to a robust anomaly-pressure score.
    persistence = min(1.0, recent_anomalies * 2.0 + anomaly_rate)
    risk = float(np.clip(0.55 * (1 - current_health / 100.0) + 0.45 * persistence, 0, 1))
    if risk >= 0.70:
        priority = "High"
        recommendation = "Inspect sensor calibration, wiring/power and mounting; schedule maintenance soon."
    elif risk >= 0.40:
        priority = "Medium"
        recommendation = "Monitor anomaly frequency and inspect the affected sensor during the next service window."
    else:
        priority = "Low"
        recommendation = "Continue monitoring; no immediate maintenance action indicated."
    return {
        "degradation_risk": round(risk, 3),
        "maintenance_priority": priority,
        "recommendation": recommendation,
        "anomaly_rate": round(anomaly_rate, 3),
        "recent_anomaly_rate": round(recent_anomalies, 3),
        "samples_analyzed": len(rows),
    }
