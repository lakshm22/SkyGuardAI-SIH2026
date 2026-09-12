# Evaluation

Run from the `backend` directory:

```bash
python evaluation/evaluate_anomaly_detection.py
```

The benchmark creates a reproducible synthetic AWS dataset containing normal observations and injected temperature, pressure, humidity, and multivariate anomalies. It reports accuracy, precision, recall, F1, specificity, false-alarm rate, and a confusion matrix.

This benchmark is intended to demonstrate the evaluation methodology required by the SIH problem statement. Results on synthetic data must not be presented as measured accuracy on real AWS observations.
