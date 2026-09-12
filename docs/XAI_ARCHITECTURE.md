# SkyGuard AI — Explainable AI Architecture

## What SHAP does

SkyGuard uses `shap.TreeExplainer` on the Isolation Forest. The model receives only:

- Temperature (°C)
- Atmospheric Pressure (hPa)
- Relative Humidity (%)

For Isolation Forest, a lower `decision_function` value is more anomalous. A negative
SHAP value therefore pushes the model toward the anomalous direction. SkyGuard converts
negative SHAP magnitude into a normalized **anomaly contribution percentage**.

These percentages are **feature contributions, not probabilities**.

## What SHAP does not do

SHAP does not independently diagnose a physical sensor failure. It explains the ML
model's decision. SkyGuard combines that explanation with:

1. temporal/seasonal deviation,
2. geographic neighbor consistency,
3. multivariate/domain rules,
4. frozen-value detection, and
5. telemetry continuity.

The evidence engine then produces the operator-facing diagnosis.

## Example

Input:

```text
Temperature = 55°C
Pressure    = 990 hPa
Humidity    = 98% RH
```

Possible explanation:

```text
Temperature       42.0% contribution
Humidity          27.0% contribution
Pressure          31.0% contribution
```

If the same station normally reports ~31°C and nearby stations remain near 31°C,
the final diagnosis can be:

> Probable temperature sensor anomaly. Temperature is the strongest SHAP contributor
> and is substantially different from the station's temporal baseline and nearby AWS
> observations.

If several nearby stations show the same temperature rise, the spatial evidence can
instead classify the event as a probable genuine regional meteorological event.

## Why this is stronger than a SHAP-only dashboard

The system answers four separate questions:

- **What happened?** — anomaly detection.
- **Why did the ML model flag it?** — SHAP feature attribution.
- **What does the anomaly most likely mean?** — temporal/spatial/domain evidence.
- **What should the operator do?** — root-cause-specific recommendation.
