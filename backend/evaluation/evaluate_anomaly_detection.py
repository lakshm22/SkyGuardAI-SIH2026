"""Reproducible evaluation on normal + injected AWS anomalies.

Run from backend/: python evaluation/evaluate_anomaly_detection.py
"""
from pathlib import Path
import sys
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.services.ml_engine import AnomalyEngine


def make_data(seed=42, n_normal=2000, n_anomaly=1000):
    rng = np.random.default_rng(seed)
    # Correlated synthetic normal weather observations.
    t = rng.normal(29, 4.5, n_normal)
    p = 1008 + rng.normal(0, 3.0, n_normal) - (t - 29) * 0.10
    h = np.clip(70 - (t - 29) * 1.4 + rng.normal(0, 7, n_normal), 15, 98)
    normal = np.column_stack([t, p, h])

    groups = []
    groups.append(np.column_stack([rng.normal(55, 2, n_anomaly//4), rng.normal(1007, 3, n_anomaly//4), rng.normal(92, 3, n_anomaly//4)]))
    groups.append(np.column_stack([rng.normal(30, 2, n_anomaly//4), rng.normal(955, 5, n_anomaly//4), rng.normal(70, 6, n_anomaly//4)]))
    groups.append(np.column_stack([rng.normal(30, 2, n_anomaly//4), rng.normal(1008, 3, n_anomaly//4), rng.normal(99, 1, n_anomaly//4)]))
    groups.append(np.column_stack([rng.normal(54, 2, n_anomaly - 3*(n_anomaly//4)), rng.normal(975, 5, n_anomaly - 3*(n_anomaly//4)), rng.normal(98, 2, n_anomaly - 3*(n_anomaly//4))]))
    anomalies = np.vstack(groups)
    return np.vstack([normal, anomalies]), np.r_[np.zeros(len(normal), dtype=int), np.ones(len(anomalies), dtype=int)]


def main():
    x, y = make_data()
    engine = AnomalyEngine(model_path=ROOT / 'models' / 'evaluation_isolation_forest.joblib')
    scores = []
    for row in x:
        score, *_ = engine.analyze(*row, explain=False)
        scores.append(score)
    scores = np.array(scores)
    pred = (scores >= 0.60).astype(int)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / max(tn + fp, 1)
    print('SkyGuard AI anomaly-injection evaluation')
    print('-----------------------------------------')
    print(f'Samples: {len(y)} (normal={sum(y==0)}, anomaly={sum(y==1)})')
    print(f'Accuracy:    {accuracy_score(y, pred):.4f}')
    print(f'Precision:   {precision_score(y, pred, zero_division=0):.4f}')
    print(f'Recall:      {recall_score(y, pred, zero_division=0):.4f}')
    print(f'F1-score:    {f1_score(y, pred, zero_division=0):.4f}')
    print(f'Specificity: {specificity:.4f}')
    print(f'False alarm rate: {1-specificity:.4f}')
    print(f'Confusion matrix [[TN, FP], [FN, TP]]: {cm.tolist()}')
    print('\nNOTE: This is a reproducible synthetic anomaly-injection benchmark, not a claim of accuracy on real AWS data.')
    try:
        (ROOT / 'models' / 'evaluation_isolation_forest.joblib').unlink(missing_ok=True)
    except Exception:
        pass

if __name__ == '__main__':
    main()
