from pathlib import Path
from datetime import datetime
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = ["temperature", "pressure", "humidity"]

class AnomalyEngine:
    """
    Hybrid detector:
    1. Physical/domain sanity checks.
    2. Isolation Forest for multivariate outliers.
    3. Temporal/neighbor deviations supplied by the service layer.
    """

    def __init__(self, model_path="./models/isolation_forest.joblib"):
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=250,
            contamination=0.02,
            random_state=42
        )
        self._train_or_load()

    def _normal_training_data(self, n=5000):
        rng = np.random.default_rng(42)
        t = rng.normal(29, 4.5, n)
        p = 1008 + rng.normal(0, 3.0, n) - (t-29)*0.10
        h = np.clip(70 - (t-29)*1.4 + rng.normal(0, 7, n), 15, 98)
        return np.column_stack([t,p,h])

    def _train_or_load(self):
        if self.model_path.exists():
            obj = joblib.load(self.model_path)
            self.scaler, self.model = obj["scaler"], obj["model"]
            return
        x = self._normal_training_data()
        self.scaler.fit(x)
        self.model.fit(self.scaler.transform(x))
        joblib.dump({"scaler":self.scaler,"model":self.model}, self.model_path)

    def predict(self, temperature, pressure, humidity):
        x = np.array([[temperature,pressure,humidity]], dtype=float)
        z = self.scaler.transform(x)
        raw = float(self.model.decision_function(z)[0])
        # Convert Isolation Forest decision function to a practical 0..1 anomaly score.
        score = float(np.clip(0.5 - raw, 0, 1))
        return score

    @staticmethod
    def domain_flags(t,p,h):
        flags={}
        flags["temperature_range"] = max(0, abs(t-29)/14)
        flags["pressure_deviation"] = max(0, abs(p-1008)/12)
        flags["humidity_extreme"] = max(0, abs(h-65)/45)
        flags["cross_parameter"] = float((t > 45 and h > 85) or (t < -5 and h > 90))
        return {k:float(np.clip(v,0,1)) for k,v in flags.items()}

    def analyze(self, t,p,h, temporal=0.0, spatial=0.0, frozen=0.0):
        ml = self.predict(t,p,h)
        flags = self.domain_flags(t,p,h)
        components = {
            "ML outlier": ml,
            "Temperature jump": flags["temperature_range"],
            "Pressure deviation": flags["pressure_deviation"],
            "Humidity inconsistency": flags["humidity_extreme"],
            "Spatial mismatch": spatial,
            "Data pattern deviation": max(temporal,frozen)
        }
        weighted = (
            0.45*ml + 0.20*flags["temperature_range"] +
            0.12*flags["pressure_deviation"] + 0.10*flags["humidity_extreme"] +
            0.08*spatial + 0.05*max(temporal,frozen)
        )
        # Domain extremes must be able to trigger an alert even when the
        # unsupervised model has not yet seen enough local history.
        domain_floor = max(
            0.80*flags["temperature_range"],
            0.72*flags["pressure_deviation"],
            0.82*flags["humidity_extreme"],
            0.90*flags["cross_parameter"],
            0.72*max(temporal,frozen)
        )
        score = float(np.clip(max(weighted, domain_floor), 0, 1))
        anomaly = score >= 0.60
        severity = "Critical" if score >= 0.82 else "Warning" if score >= 0.60 else "Normal"
        confidence = float(np.clip(0.50 + score*0.50, 0, 0.99))
        ranked = sorted(components.items(), key=lambda x:x[1], reverse=True)
        root = self._root_cause(ranked, t,p,h,spatial,frozen)
        return score,confidence,severity,anomaly,root,components

    def _root_cause(self, ranked,t,p,h,spatial,frozen):
        top = ranked[0][0]
        if frozen > .7: return "Frozen sensor / repeated value"
        if top == "Temperature jump": return "Temperature sensor malfunction"
        if top == "Spatial mismatch": return "Localized sensor fault or transmission error"
        if top == "Pressure deviation": return "Pressure sensor drift"
        if top == "Humidity inconsistency": return "Humidity sensor inconsistency"
        if top == "Data pattern deviation": return "Temporal pattern deviation"
        return "Multivariate sensor anomaly"
