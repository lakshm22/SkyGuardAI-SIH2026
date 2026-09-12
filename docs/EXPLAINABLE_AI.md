# Explainable AI in SkyGuard AI

SkyGuard uses two complementary explanation layers.

## 1. Hybrid evidence explanation

The detector exposes component scores for:

- Isolation Forest multivariate outlier score
- Temperature deviation
- Pressure deviation
- Humidity inconsistency
- Temporal/seasonal deviation
- Spatial mismatch
- Frozen-value evidence
- Communication gap evidence

These scores are converted into a human-readable explanation and root-cause classification.

## 2. SHAP feature attribution

For the tree-based Isolation Forest, SkyGuard attempts to generate SHAP feature attribution for the three meteorological inputs. The dashboard displays normalized relative contributions when SHAP is available.

Example interpretation:

```text
Temperature 62.3%
Humidity    31.6%
Pressure     6.1%
```

This means temperature contributed the most to the model's multivariate outlier decision for that observation. It does not mean that the sensor is 62.3% faulty.

## Why this matters

The operator can see not only that an anomaly was detected, but also which input variables and consistency checks drove the decision. This reduces black-box behavior and supports human verification before maintenance or data correction.
