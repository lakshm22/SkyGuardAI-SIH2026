"""Explainable-AI layer for SkyGuard.

SHAP explains the Isolation Forest decision.  Domain, temporal and spatial
signals are then combined into an operator-facing diagnosis.  This separation
is intentional: SHAP explains *what the ML model saw*; the evidence engine
explains *what the observation most likely means operationally*.
"""
from __future__ import annotations

import numpy as np

try:
    import shap
except Exception:  # pragma: no cover
    shap = None

FEATURES = ["Temperature", "Pressure", "Humidity"]


def shap_explanation(model, scaler, temperature, pressure, humidity):
    """Return signed and normalized SHAP attribution for an Isolation Forest.

    IsolationForest's decision_function is higher for normal observations.
    Therefore a negative SHAP value pushes the decision toward *more anomalous*.
    We expose both the signed contribution and a normalized anomaly-contribution
    percentage so the UI never misrepresents SHAP values as probabilities.
    """
    result = {
        "available": False,
        "method": "SHAP TreeExplainer",
        "features": [],
        "top_feature": None,
    }
    if shap is None:
        result["reason"] = "SHAP is not installed."
        return result
    try:
        x = np.array([[temperature, pressure, humidity]], dtype=float)
        z = scaler.transform(x)
        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(z)
        if isinstance(values, list):
            values = values[0]
        values = np.asarray(values, dtype=float).reshape(-1)
        if values.size != 3 or not np.all(np.isfinite(values)):
            result["reason"] = "Unexpected SHAP output shape."
            return result

        # For IsolationForest, negative SHAP pushes decision_function downward,
        # which is the anomalous direction.
        anomaly_push = np.maximum(-values, 0.0)
        total = float(anomaly_push.sum())
        if total <= 1e-12:
            anomaly_pct = np.zeros(3)
        else:
            anomaly_pct = anomaly_push / total

        features = []
        for feature, signed, contribution in zip(FEATURES, values, anomaly_pct):
            features.append({
                "feature": feature,
                "shap_value": round(float(signed), 6),
                "anomaly_contribution": round(float(contribution), 6),
                "anomaly_contribution_pct": round(float(contribution * 100), 2),
                "direction": "toward anomaly" if signed < 0 else "toward normal",
            })
        features.sort(key=lambda x: x["anomaly_contribution"], reverse=True)
        result.update({
            "available": True,
            "features": features,
            "top_feature": features[0]["feature"] if features else None,
            "baseline_value": float(np.asarray(explainer.expected_value).reshape(-1)[0]),
        })
        return result
    except Exception as exc:  # pragma: no cover - version/platform dependent
        result["reason"] = f"SHAP attribution unavailable: {type(exc).__name__}"
        return result


def _top_components(components):
    return sorted(components.items(), key=lambda kv: kv[1], reverse=True)


def build_explanation(*, root_cause, temporal, spatial_info, components, shap_info,
                      baseline=None, corrected=None, communication_gap_seconds=None,
                      frozen=0.0):
    """Create structured evidence plus a concise operator-facing explanation."""
    spatial_score = float(spatial_info.get("score", 0.0))
    regional_event = bool(spatial_info.get("regional_event"))
    isolated = bool(spatial_info.get("isolated"))
    top_components = _top_components(components)
    top_feature = shap_info.get("top_feature") if shap_info else None

    evidence = []
    if top_feature:
        evidence.append(f"{top_feature} is the strongest SHAP contributor to the model decision.")
    if temporal >= 0.60:
        evidence.append("The observation is substantially different from its learned temporal/seasonal baseline.")
    if spatial_score >= 0.60 and isolated:
        evidence.append("The reading differs substantially from geographically nearby AWS observations.")
    if regional_event:
        evidence.append("Nearby stations show a consistent deviation, supporting a regional meteorological event rather than an isolated sensor fault.")
    if frozen >= 0.70:
        evidence.append("Recent telemetry contains repeated identical values, indicating a possible frozen sensor.")
    if communication_gap_seconds is not None and communication_gap_seconds >= 180:
        evidence.append(f"No valid telemetry was received for approximately {communication_gap_seconds:.0f} seconds.")

    if root_cause == "Temperature sensor malfunction":
        summary = "Probable temperature sensor anomaly."
        action = "Inspect temperature-sensor calibration, wiring and physical placement."
    elif root_cause == "Pressure sensor drift":
        summary = "Probable pressure sensor anomaly or calibration drift."
        action = "Verify pressure-sensor calibration and inspect the sensor for drift."
    elif root_cause == "Humidity sensor inconsistency":
        summary = "Probable humidity sensor anomaly."
        action = "Inspect humidity-sensor calibration and environmental exposure."
    elif root_cause == "Frozen sensor / repeated value":
        summary = "Probable frozen or stuck sensor output."
        action = "Inspect the sensor interface and verify that measurements are changing normally."
    elif root_cause == "Communication / telemetry gap":
        summary = "Probable telemetry or communication failure."
        action = "Check the station gateway, network link, power supply and last-seen device status."
    elif root_cause == "Probable regional meteorological event":
        summary = "Probable genuine regional meteorological event."
        action = "Continue monitoring regional observations; do not automatically discard the reading as a sensor fault."
    else:
        summary = f"Probable {root_cause.lower()}."
        action = "Inspect the station and continue monitoring subsequent observations."

    if not evidence:
        evidence.append("The hybrid detector found the observation outside its learned operating pattern.")

    details = " ".join(evidence)
    if corrected and root_cause != "Probable regional meteorological event":
        details += (
            f" An AI-assisted corrected estimate is available: "
            f"{corrected['temperature']:.1f}°C, {corrected['pressure']:.1f} hPa, "
            f"{corrected['humidity']:.1f}% RH."
        )

    return {
        "summary": summary,
        "primary_ml_driver": top_feature,
        "details": details,
        "recommended_action": action,
        "top_evidence": [{"name": k, "score": round(float(v), 3)} for k, v in top_components[:5]],
        "shap": shap_info,
        "temporal_score": round(float(temporal), 3),
        "spatial_score": round(spatial_score, 3),
        "spatial_context": spatial_info,
        "baseline": baseline,
        "corrected_values": corrected,
        "communication_gap_seconds": communication_gap_seconds,
    }


def reasoning_text(root_cause, temporal, spatial, components, shap_values=None, regional_event=False):
    """Backward-compatible compact explanation string."""
    ranked = _top_components(components)
    top = ", ".join(f"{k}={v:.2f}" for k, v in ranked[:3])
    event_text = (
        "Nearby stations show a similar deviation, supporting a regional meteorological event."
        if regional_event else
        "The deviation is comparatively localized, increasing the likelihood of a station or sensor issue."
    )
    shap_text = (
        "SHAP feature attribution identifies the relative contribution of the meteorological inputs."
        if shap_values else
        "The explanation falls back to hybrid evidence because SHAP attribution was unavailable."
    )
    return f"Probable cause: {root_cause}. Top evidence: {top}. Temporal deviation={temporal:.2f}; spatial deviation={spatial:.2f}. {event_text} {shap_text}"
