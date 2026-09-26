# 🚀 SkyGuard AI

### AI-Powered Anomaly Detection and Data-Quality Monitoring System for Automatic Weather Stations

**Smart India Hackathon (SIH) 2026 Project**

SkyGuard AI is an intelligent monitoring platform designed to detect, analyze, explain, and visualize abnormal behavior in **Automatic Weather Stations (AWS)** using **Machine Learning, statistical analysis, temporal patterns, spatial consistency, and domain-based rules**.

The system processes weather-station telemetry consisting of:

* 🌡️ Temperature
* 🌡️ Atmospheric pressure
* 💧 Relative humidity

SkyGuard AI combines multiple anomaly-detection signals to distinguish between **genuine environmental variations and potential sensor/data-quality problems**, while providing operators with an interpretable anomaly score, severity classification, sensor-health information, and real-time visualization.

---

# 📌 Problem Statement

Automatic Weather Stations continuously generate large volumes of environmental observations. Faulty sensors, communication errors, calibration drift, corrupted data, and unusual environmental conditions can produce abnormal or inconsistent readings.

Traditional monitoring systems often rely heavily on fixed threshold-based alerts.

This can result in:

* **False alarms** caused by temporary fluctuations.
* **Missed anomalies** that do not violate a predefined threshold.
* Difficulty distinguishing genuine weather events from sensor failures.
* Limited visibility into why a reading was considered abnormal.

There is therefore a need for an intelligent monitoring system capable of evaluating sensor observations using multiple contextual signals.

SkyGuard AI addresses this by analyzing:

* Normal environmental variations
* Sensor faults
* Communication/data-quality issues
* Sudden abnormal events
* Persistent anomalies
* Temporal inconsistencies
* Spatially inconsistent measurements
* Multivariate relationships between weather parameters

---

# 💡 Proposed Solution

SkyGuard AI combines **Machine Learning with deterministic domain knowledge** to provide intelligent AWS monitoring.

Instead of depending on a single threshold or ML prediction, the system evaluates multiple signals before producing an anomaly assessment.

```text
                         AWS Telemetry
                              │
                              ▼
                    ┌──────────────────┐
                    │ Data Validation  │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Feature Processing  │
                  └──────────┬───────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
         ML Detection   Rule Engine   Time Analysis
                │            │            │
                └────────────┼────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Hybrid Scoring  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Severity Level  │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
           Alert Generation        Dashboard
```

---

# 🎯 Key Objectives

* Detect anomalous AWS sensor readings automatically.
* Reduce dependence on fixed threshold-only monitoring.
* Identify abnormal patterns across multiple weather parameters.
* Detect sudden and persistent anomalies.
* Identify temporal and spatial inconsistencies.
* Monitor sensor and station health.
* Assess data quality.
* Provide explainable anomaly analysis.
* Visualize station conditions in real time.
* Store historical telemetry and anomaly information.
* Provide an architecture that can be extended to physical AWS deployments.

---

# ⭐ Key Features

## 1. 🤖 AI-Based Anomaly Detection

SkyGuard AI uses **Isolation Forest**, an unsupervised anomaly-detection algorithm, to identify observations that differ significantly from normal telemetry patterns.

The model can analyze multiple weather parameters together rather than evaluating each parameter independently.

```text
Temperature
     +
Pressure
     +
Humidity
     ↓
Feature Processing
     ↓
Isolation Forest
     ↓
Anomaly Detection
```

---

## 2. 🧠 Hybrid Anomaly Detection

Machine Learning is combined with deterministic domain rules and contextual analysis.

The system considers signals such as:

* ML anomaly output
* Sensor-range violations
* Rate of change
* Temporal behavior
* Spatial consistency
* Multivariate relationships
* Data-quality checks
* Sensor consistency

This provides additional context beyond an isolated ML prediction.

---

## 3. 📈 Temporal Analysis

The system analyzes sensor behavior across time.

### Normal

```text
25.0°C → 25.2°C → 25.4°C → 25.6°C
```

### Potential Anomaly

```text
25.0°C → 25.3°C → 25.5°C → 80.0°C
```

A sudden change can be identified by evaluating the observation against its temporal context rather than considering the current value alone.

---

## 4. 🌍 Spatial Analysis

Multiple AWS stations can be distributed across different geographical locations.

SkyGuard AI can use neighboring station observations to identify spatial inconsistencies.

Example:

```text
Station A → 31°C
Station B → 30°C
Station C → 30.5°C
Station D → 75°C  ← Potential anomaly
```

Spatial comparison provides an additional signal when determining whether an observation is consistent with surrounding stations.

---

## 5. 🚨 Severity Classification

Detected anomalies are categorized according to their severity.

| Severity        | Meaning                                          |
| --------------- | ------------------------------------------------ |
| 🟢 **Normal**   | No significant anomaly detected                  |
| 🟡 **Warning**  | Significant anomaly requiring attention          |
| 🔴 **Critical** | Severe anomaly requiring immediate investigation |

The exact classification is determined by the application's anomaly-scoring and rule-evaluation logic.

---

## 6. 🔎 Explainable AI with SHAP

SkyGuard AI incorporates **SHAP (SHapley Additive exPlanations)** to provide feature-level explanations for supported model outputs.

Instead of displaying only:

```text
Anomaly Detected
```

the system can provide additional information about the contribution of the monitored variables.

Example:

```text
Anomaly Detected

Contributing Features:
• Relative Humidity → High contribution
• Temperature      → Moderate contribution
• Pressure         → Low contribution
```

This makes the anomaly-detection process more interpretable for operators.

> **Important:** SHAP explains model outputs; it does not itself determine whether a weather observation is correct or incorrect.

---

## 7. 📊 Interactive Monitoring Dashboard

The web dashboard provides a centralized view of AWS infrastructure.

It includes:

* AWS station locations
* Station status
* Temperature trends
* Pressure trends
* Humidity trends
* Anomaly indicators
* Anomaly severity
* Historical telemetry
* Sensor health
* Alerts
* Anomaly analytics

---

## 8. 🗺️ Geographic Station Map

The dashboard provides geographical visualization of AWS stations using **Leaflet**.

Operators can identify:

* Station locations
* Station status
* Active anomalies
* Affected geographical regions
* Spatial relationships between stations

---

## 9. 📉 Trend Visualization

Historical and live observations can be visualized through interactive charts using **Recharts**.

Supported parameters include:

* Temperature
* Atmospheric pressure
* Relative humidity
* Anomaly score

This helps operators determine whether an anomaly is isolated, sudden, or part of a longer-term pattern.

---

# 🏗️ System Architecture

```text
                     ┌─────────────────────┐
                     │ Automatic Weather   │
                     │ Stations / Sensors  │
                     └──────────┬──────────┘
                                │
                         MQTT / JSON
                                │
                                ▼
                     ┌─────────────────────┐
                     │   FastAPI Backend   │
                     │                     │
                     │ Data Validation     │
                     │ Authentication      │
                     │ API Processing      │
                     └──────────┬──────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │   Analytics / AI Layer │
                    │                        │
                    │ Isolation Forest       │
                    │ Rule-Based Checks      │
                    │ Temporal Analysis      │
                    │ Spatial Analysis       │
                    │ Multivariate Analysis  │
                    │ SHAP Explainability    │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Anomaly Score &         │
                    │ Severity Assessment     │
                    └───────────┬────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
          ┌──────────────────┐    ┌──────────────────┐
          │ PostgreSQL /     │    │ React + TypeScript│
          │ Supabase         │    │ Dashboard         │
          └──────────────────┘    └────────┬─────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │    Operator     │
                                  └─────────────────┘
```

---

# 🔄 Data Flow

```text
AWS Sensor
    ↓
MQTT / JSON Telemetry
    ↓
Data Ingestion
    ↓
Data Validation
    ↓
Feature Processing
    ↓
┌────────────────────────────┐
│ Isolation Forest            │
│ Domain Rules                │
│ Temporal Analysis           │
│ Spatial Analysis            │
│ Multivariate Checks         │
└─────────────┬──────────────┘
              ↓
       Hybrid Anomaly Score
              ↓
       Severity Classification
              ↓
       SHAP Explanation
              ↓
       Sensor Health Analysis
              ↓
       PostgreSQL / Supabase
              ↓
          FastAPI REST API
              ↓
      React Monitoring UI
              ↓
       Operator Dashboard
```

---

# 🧠 Machine Learning Approach

## Isolation Forest

SkyGuard AI uses **Isolation Forest** for unsupervised anomaly detection.

This approach is useful because AWS datasets may not contain sufficient labelled examples for every possible type of sensor failure.

Instead of requiring every anomaly type to be explicitly labelled:

```text
Historical / Normal Telemetry
          ↓
   Feature Processing
          ↓
    Isolation Forest
          ↓
Identify Unusual Observations
          ↓
   Anomaly Assessment
```

### Why Isolation Forest?

| Requirement                         | Isolation Forest |
| ----------------------------------- | ---------------- |
| Requires labelled anomaly data      | ❌ No             |
| Designed for anomaly detection      | ✅ Yes            |
| Supports multivariate features      | ✅ Yes            |
| Suitable for unsupervised detection | ✅ Yes            |
| Computationally practical           | ✅ Yes            |

---

# 🧮 Hybrid Anomaly Scoring

The final anomaly assessment is **not based solely on the Isolation Forest output**.

Conceptually:

```text
              ML Signal
                  +
           Rule-Based Signal
                  +
          Temporal Signal
                  +
       Spatial / Consistency Signal
                  ↓
        ┌───────────────────┐
        │ Hybrid Assessment │
        └─────────┬─────────┘
                  ↓
           Anomaly Score
                  ↓
        Severity Classification
```

The resulting **anomaly score represents the system's assessment of abnormality**.

It should **not be interpreted as a probability or model-confidence percentage** unless a separate calibrated probabilistic model has been implemented.

---

# 🛠️ Technology Stack

## Frontend

| Technology       | Purpose                               |
| ---------------- | ------------------------------------- |
| **React**        | Component-based user interface        |
| **TypeScript**   | Type-safe frontend development        |
| **Vite**         | Development server and build tooling  |
| **Tailwind CSS** | UI styling and responsive layouts     |
| **Recharts**     | Sensor and anomaly data visualization |
| **Leaflet**      | Interactive geographical station map  |

---

## Backend

| Technology     | Purpose                          |
| -------------- | -------------------------------- |
| **Python**     | Backend and ML ecosystem         |
| **FastAPI**    | REST API and backend application |
| **Pydantic**   | Request/response data validation |
| **SQLAlchemy** | Database ORM and abstraction     |
| **Uvicorn**    | ASGI application server          |

---

## AI / Machine Learning

| Technology                 | Purpose                             |
| -------------------------- | ----------------------------------- |
| **Scikit-learn**           | Machine-learning framework          |
| **Isolation Forest**       | Unsupervised anomaly detection      |
| **SHAP**                   | Model explainability                |
| **Feature-based analysis** | Multivariate anomaly analysis       |
| **Rule-based validation**  | Domain-specific data-quality checks |
| **Temporal analysis**      | Time-dependent anomaly detection    |
| **Spatial analysis**       | Cross-station consistency analysis  |

---

## Database

| Technology     | Purpose                                       |
| -------------- | --------------------------------------------- |
| **PostgreSQL** | Relational data storage                       |
| **Supabase**   | Managed PostgreSQL and backend infrastructure |

---

## Communication

| Technology   | Purpose                                         |
| ------------ | ----------------------------------------------- |
| **MQTT**     | Lightweight IoT publish/subscribe communication |
| **JSON**     | Sensor telemetry data format                    |
| **REST API** | Frontend-backend communication                  |

---

## Deployment

| Technology   | Purpose                                 |
| ------------ | --------------------------------------- |
| **Render**   | Backend / application deployment        |
| **Supabase** | Managed PostgreSQL infrastructure       |
| **GitHub**   | Source-code hosting and version control |

---

# 📡 Communication Architecture

The system is designed to support telemetry transmission using MQTT.

```text
AWS / ESP32
     │
     │ MQTT
     ▼
 MQTT Broker
     │
     │ JSON
     ▼
FastAPI Backend
     │
     ▼
Analytics Pipeline
```

Example telemetry:

```json
{
  "station_id": "AWS_001",
  "temperature": 31.4,
  "pressure": 1008.7,
  "humidity": 72.5,
  "timestamp": "2026-09-26T12:30:00Z"
}
```

The same architecture can support simulated telemetry for a software-only demonstration while remaining compatible with future physical sensor deployment.

---

# 📁 Project Structure

```text
SkyGuard-AI/
│
├── README.md
│
├── backend/
│   ├── README.md
│   ├── FRONTEND_INTEGRATION.md
│   ├── requirements.txt
│   ├── run.py
│   ├── .env.example
│   ├── .gitignore
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   ├── report.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── anomaly_service.py
│   │       ├── advanced_analytics.py
│   │       ├── explainability.py
│   │       ├── ml_engine.py
│   │       └── monitor.py
│   │
│   ├── simulator/
│   │   ├── __init__.py
│   │   ├── stream.py
│   │   ├── demo_runbook.py
│   │   └── README.md
│   │
│   ├── evaluation/
│   │   ├── evaluate_anomaly_detection.py
│   │   └── README.md
│   │
│   ├── models/
│   │   └── isolation_forest.joblib
│   │
│   └── data/
│       └── skyguard.db
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── .prettierrc
│   ├── .gitignore
│   ├── bunfig.toml
│   ├── components.json
│   ├── render.yaml
│   ├── README.md
│   │
│   ├── public/
│   │
│   └── src/
│       ├── router.tsx
│       ├── server.ts
│       ├── start.ts
│       ├── routeTree.gen.ts
│       ├── styles.css
│       │
│       ├── routes/
│       │   ├── __root.tsx
│       │   ├── index.tsx
│       │   └── README.md
│       │
│       ├── components/
│       │   ├── skyguard/
│       │   │   ├── api-settings.tsx
│       │   │   ├── network-map.tsx
│       │   │   ├── panel.tsx
│       │   │   └── trend-chart.tsx
│       │   │
│       │   └── ui/
│       │       └── ...
│       │
│       ├── hooks/
│       │   └── use-mobile.tsx
│       │
│       └── lib/
│           ├── utils.ts
│           ├── error-capture.ts
│           ├── error-page.ts
│           └── skyguard-api.ts
│
├── docs/
│   ├── EXPLAINABLE_AI.md
│   ├── XAI_ARCHITECTURE.md
│   ├── SIH_COMPLIANCE.md
│   ├── SOFTWARE_ONLY_DEMO.md
│   ├── SIH_USE_CASES.md
│   ├── REAL_AWS_STREAMING.md
│   └── LIVE_GRAPH_FIX.md
│
└── esp32/
    ├── README.md
    └── skyguard_esp32_bme280.ino
```

---

# ⚙️ Installation

## Prerequisites

Install:

* **Python 3.10+**
* **Node.js 18+**
* **npm**
* **Git**
* **PostgreSQL / Supabase account**

---

# 🔧 Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/lakshm22/SkyGuardAI-SIH2026.git
cd SkyGuardAI-SIH2026
```

### 2. Navigate to Backend

```bash
cd backend
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file inside the `backend` directory.

Example:

```env
DATABASE_URL=your_database_connection_string

SKYGUARD_ADMIN_USERNAME=admin
SKYGUARD_ADMIN_PASSWORD=your_secure_password

CORS_ORIGINS=http://localhost:5173
```

> ⚠️ Never commit `.env` or production credentials to GitHub.

Use `.env.example` to document required environment variables.

---

# ▶️ Run Backend

From the `backend` directory:

```bash
python run.py
```

The API will normally be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

---

# 💻 Frontend Setup

Open another terminal.

### 1. Navigate to Frontend

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔌 API Architecture

The React frontend communicates with the FastAPI backend through REST APIs.

```text
React + TypeScript
        │
        │ HTTP / REST
        ▼
     FastAPI
        │
        ▼
   Service Layer
        │
 ┌──────┼─────────┐
 ▼      ▼         ▼
ML   Analytics  Database
 │      │         │
 └──────┴─────────┘
        │
        ▼
   PostgreSQL
```

This separation keeps:

* Presentation logic
* API logic
* Business logic
* Machine-learning logic
* Database operations

independently manageable.

---

# 🔒 Security

The system incorporates:

* Authentication for protected dashboard access
* Environment variables for secrets
* Password protection
* CORS configuration
* API-level validation
* SQLAlchemy database abstraction
* No hard-coded production credentials

### Recommended Production Enhancements

* HTTPS
* Strong password policies
* Secret management
* Rate limiting
* Role-based access control
* Audit logging

---

# 🚨 Example Anomaly Scenario

Suppose an AWS normally reports:

```text
Temperature: 27°C
Pressure:    1012 hPa
Humidity:    65%
```

Suddenly, it reports:

```text
Temperature: 91°C
Pressure:    1011 hPa
Humidity:    64%
```

SkyGuard AI evaluates multiple signals:

```text
Temperature Deviation
        +
ML Anomaly Signal
        +
Temporal Change
        +
Multivariate Consistency
        +
Domain Rules
        ↓
Potential Anomaly
        ↓
Anomaly Score
        ↓
Severity Classification
        ↓
SHAP Explanation
```

The operator can then investigate the affected station.

---

# 📊 Dashboard Architecture

```text
┌───────────────────────────────────────────────┐
│                 SKYGUARD AI                   │
├───────────────────────────────────────────────┤
│                                               │
│  Total Stations    Active Alerts    Health   │
│       XX                XX            XX%     │
│                                               │
├───────────────────────┬───────────────────────┤
│                       │                       │
│     Station Map       │    Sensor Trends     │
│                       │                       │
│                       │                       │
├───────────────────────┴───────────────────────┤
│                                               │
│              Anomaly Monitoring               │
│                                               │
└───────────────────────────────────────────────┘
```

---

# 📈 Advantages of the Approach

### Traditional Threshold-Based Monitoring

```text
Sensor
  ↓
Fixed Threshold
  ↓
Alert
```

### SkyGuard AI

```text
Sensor
  ↓
Data Validation
  ↓
Feature Processing
  ↓
┌────────────────────────┐
│ ML Detection           │
│ Domain Rules           │
│ Temporal Analysis      │
│ Spatial Analysis       │
│ Multivariate Analysis  │
└────────────┬───────────┘
             ↓
       Hybrid Assessment
             ↓
        Anomaly Score
             ↓
          Severity
             ↓
        Explanation
             ↓
           Alert
```

The approach provides multiple contextual signals instead of relying exclusively on a single fixed threshold.

---

# 🧪 Testing & Evaluation

SkyGuard AI includes an evaluation module for testing anomaly-detection behavior.

Example normal telemetry:

```json
{
  "temperature": 28.5,
  "pressure": 1012.4,
  "humidity": 67.2
}
```

Example abnormal telemetry:

```json
{
  "temperature": 89.7,
  "pressure": 1011.8,
  "humidity": 66.5
}
```

The system evaluates the observation using its anomaly-detection pipeline and generates the corresponding anomaly assessment.

> **Evaluation metrics should only be reported when supported by an appropriate labelled test dataset or documented evaluation methodology.**

---

# 🚀 Future Scope

The architecture can be extended with:

* Real-time MQTT telemetry ingestion
* Physical AWS/ESP32 deployments
* Advanced time-series models
* LSTM / Autoencoder-based anomaly detection
* Automated sensor-fault classification
* SMS / Email notifications
* Mobile application
* Edge-based anomaly detection
* Predictive maintenance
* Automated model retraining
* Advanced geospatial anomaly detection
* Role-based access control
* Long-term sensor reliability analytics

---

# ☁️ Deployment

## Backend

The FastAPI backend can be deployed using **Render**.

## Database

Production data can be stored using **Supabase PostgreSQL**.

## Frontend

The React/Vite frontend can be deployed using a suitable static/web hosting platform.

---

# 🌐 Production Architecture

```text
                         INTERNET
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          React Frontend          AWS / ESP32
                 │                     │
                 │ REST API            │ MQTT
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    FastAPI Backend
                         Render
                            │
                            ▼
                       SQLAlchemy
                            │
                            ▼
                   Supabase PostgreSQL
```

---

# 🏆 SIH Relevance

SkyGuard AI addresses intelligent monitoring of distributed Automatic Weather Station infrastructure through:

* Artificial Intelligence
* Machine Learning
* Anomaly Detection
* Explainable AI
* Real-Time Monitoring
* Sensor Reliability Analysis
* Data-Quality Monitoring
* Geospatial Visualization
* Cloud-Ready Architecture
* IoT Communication

The architecture is designed to support both **software-based demonstration** and future integration with physical AWS/ESP32 telemetry sources.

---

# 📚 References

## Research Publications

### 1. Isolation Forest

Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2012). **Isolation-based anomaly detection.** *ACM Transactions on Knowledge Discovery from Data, 6*(1), Article 3, 1–39.

**DOI:** https://doi.org/10.1145/2133360.2133363

---

### 2. SHAP

Lundberg, S. M., & Lee, S.-I. (2017). **A Unified Approach to Interpreting Model Predictions.** *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*, 4765–4774.

**Publication:** https://papers.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html

**Paper:** https://papers.neurips.cc/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf

---

## Standards & Protocols

### 3. MQTT Version 5.0

OASIS. (2019). **MQTT Version 5.0.** OASIS Standard, 7 March 2019.

**Official Specification:** https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html

---

## Weather & Data-Quality References

### 4. NOAA — Automated Weather Observing Systems

National Centers for Environmental Information (NCEI), National Oceanic and Atmospheric Administration (NOAA). **Automated Surface/Weather Observing Systems.**

**Official Resource:** https://www.ncei.noaa.gov/products/land-based-station/automated-surface-weather-observing-system

---

### 5. NOAA — Integrated Surface Database

National Centers for Environmental Information (NCEI), NOAA. **Integrated Surface Database (ISD).**

**Official Resource:** https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database

This resource is relevant to the project's data-quality methodology because the NCEI documentation describes quality-control procedures applied to land-based station observations.

---

# 📖 Official Technical Documentation

### Frontend

* **React:** https://react.dev/
* **TypeScript:** https://www.typescriptlang.org/docs/
* **Vite:** https://vite.dev/guide/
* **Tailwind CSS:** https://tailwindcss.com/docs
* **Recharts:** https://recharts.org/
* **Leaflet:** https://leafletjs.com/reference.html

### Backend

* **Python:** https://docs.python.org/3/
* **FastAPI:** https://fastapi.tiangolo.com/
* **Pydantic:** https://docs.pydantic.dev/
* **SQLAlchemy:** https://docs.sqlalchemy.org/
* **Uvicorn:** https://www.uvicorn.org/

### Machine Learning / Explainability

* **Scikit-learn:** https://scikit-learn.org/stable/
* **Isolation Forest:** https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
* **SHAP:** https://shap.readthedocs.io/

### Database

* **PostgreSQL:** https://www.postgresql.org/docs/
* **Supabase:** https://supabase.com/docs

### Communication

* **MQTT Version 5.0:** https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html

---

# 👥 Team

## Team Name: Elementalists

| Team Member                | Role                    |      Hours |
| -------------------------- | ----------------------- | ---------: |
| **Lakshitha Mathiyalagan** | Team Lead / Backend     |  **8 hrs** |
| **Lathika S**              | AI/ML                   |  **7 hrs** |
| **Malathi S**              | Frontend                |  **6 hrs** |
| **Keerthanapriya V C**     | Testing / Documentation |  **5 hrs** |
| **Lakshana M**             | Database / Cloud        |  **5 hrs** |
| **Mahalakshmi M**          | Research / Integration  |  **5 hrs** |
| **Total**                  |                         | **36 hrs** |


**Smart India Hackathon 2026**

---

# 📜 License

This project was developed as part of the **Smart India Hackathon (SIH) 2026**.

Add an open-source license if the repository is intended for public distribution.

---

<p align="center">
  <b>SkyGuard AI — Intelligent Monitoring for Smarter Weather Stations</b>
</p>
