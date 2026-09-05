🚀 SkyGuard AI
AI-Powered Anomaly Detection and Monitoring System for Automatic Weather Stations

*Smart India Hackathon (SIH) Project*
SkyGuard AI is an intelligent monitoring platform designed to detect, analyze, and visualize abnormal behavior in **Automatic Weather Stations (AWS)** using **Machine Learning, statistical analysis, temporal patterns, and domain-based rules**.

The system continuously processes weather-station telemetry such as **temperature, pressure, humidity, wind speed, and other sensor parameters**, identifies abnormal readings, evaluates their severity, and presents the results through a centralized web dashboard.

📌 Problem Statement
Automatic Weather Stations generate large volumes of sensor data continuously. Faulty sensors, communication errors, environmental disturbances, calibration problems, and unusual weather conditions can produce abnormal or inconsistent readings.

Traditional monitoring systems generally rely on fixed threshold-based alerts.

This creates two major problems:
*False alarms** caused by temporary fluctuations.
*Missed anomalies** that do not cross a predefined threshold.

There is therefore a need for an intelligent system that can automatically identify abnormal sensor behavior and distinguish between:

* Normal environmental variations
* Sensor faults
* Communication/data-quality issues
* Sudden abnormal events
* Persistent anomalies
* Spatially inconsistent measurements

💡 Proposed Solution

**SkyGuard AI** combines Machine Learning with domain knowledge to provide intelligent AWS monitoring.

Instead of depending only on fixed thresholds, the system evaluates telemetry using multiple signals:

                    AWS Telemetry
                          │
                          ▼
                ┌──────────────────┐
                │ Data Validation   │
                └────────┬─────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Feature Processing   │
              └──────────┬───────────┘
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        ML Detection  Rule Engine  Time Analysis
             │           │           │
             └───────────┼───────────┘
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
        Alert Generation       Dashboard

🎯 Key Objectives

* Detect anomalous AWS sensor readings automatically.
* Reduce false positives compared with simple threshold systems.
* Identify abnormal patterns across multiple parameters.
* Detect persistent and sudden anomalies.
* Monitor sensor health and data quality.
* Provide real-time visualization of station conditions.
* Display anomaly severity and affected stations.
* Store historical telemetry and anomaly information.
* Provide an extensible architecture for future AWS deployments.

⭐ Key Features

1. 🤖 AI-Based Anomaly Detection

SkyGuard AI uses an **Isolation Forest** model to identify observations that differ significantly from normal telemetry patterns.
The model can detect anomalies across multiple sensor parameters instead of evaluating each value independently.

2. 🧠 Hybrid Anomaly Detection
Machine Learning is combined with deterministic domain rules.
The system considers:

* ML anomaly score
* Sensor threshold violations
* Rate of change
* Temporal behavior
* Multivariate relationships
* Data quality
* Sensor consistency

This provides a more reliable anomaly decision than using ML alone.

3. 📈 Temporal Analysis
The system analyzes sensor behavior over time.

For example:
Normal:

25°C → 25.2°C → 25.4°C → 25.6°C

Potential anomaly:

25°C → 25.3°C → 25.5°C → 80°C

A sudden unrealistic change can be flagged even when a simple static threshold might not provide enough context.

4.🌍 Spatial Analysis

AWS stations can be distributed across different geographical locations.

SkyGuard AI can compare nearby stations to identify spatial inconsistencies.

For example:
Station A → 31°C
Station B → 30°C
Station C → 30.5°C
Station D → 75°C  ← Potential anomaly

This helps identify potentially faulty sensors or abnormal measurements.

5. 🚨 Severity Classification
Detected anomalies are categorized according to their severity.

Example:

| Severity         | Meaning                                 |
| ---------------- | --------------------------------------- |
| 🟢 Normal        | Expected sensor behavior                |
| 🟡 Low           | Minor abnormality                       |
| 🟠 Medium        | Significant anomaly requiring attention |
| 🔴 High/Critical | Severe or potentially faulty condition  |

6. 📊 Interactive Dashboard
The frontend provides a centralized monitoring dashboard with:

* AWS station locations
* Sensor status
* Temperature trends
* Pressure trends
* Anomaly indicators
* Historical data
* Severity information
* Station health
* Alerts

7. 🗺️ Network/Station Map
The dashboard provides a geographical visualization of AWS stations.
Users can identify:

* Station locations
* Station status
* Active anomalies
* Affected geographical regions

 8. 📉 Trend Visualization
Historical sensor readings can be visualized through charts.
Example parameters include:

* Temperature
* Pressure
* Humidity
* Wind speed
* Anomaly score

This helps operators understand whether an anomaly is isolated or part of a larger trend.

🏗️ System Architecture


                        ┌─────────────────────┐
                        │ Automatic Weather   │
                        │ Stations (AWS)      │
                        └──────────┬──────────┘
                                   │
                             Telemetry Data
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
                       ┌──────────────────────┐
                       │ Anomaly Detection    │
                       │                      │
                       │ Isolation Forest     │
                       │ Domain Rules         │
                       │ Temporal Analysis    │
                       │ Spatial Analysis     │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ Anomaly Score &      │
                       │ Severity Assessment  │
                       └──────────┬───────────┘
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
           ┌──────────────────┐       ┌──────────────────┐
           │   PostgreSQL /   │       │   React + Vite   │
           │     Supabase     │       │    Dashboard     │
           └──────────────────┘       └────────┬─────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │     Operator    │
                                      └─────────────────┘

🔄 Data Flow

AWS Sensor
    ↓
Telemetry Ingestion
    ↓
Data Validation
    ↓
Feature Extraction
    ↓
Machine Learning Model
    ↓
Domain Rule Evaluation
    ↓
Hybrid Anomaly Score
    ↓
Severity Classification
    ↓
Database Storage
    ↓
REST API
    ↓
Web Dashboard
    ↓
Operator Alert

🧠 Machine Learning Approach
Isolation Forest

SkyGuard AI uses the **Isolation Forest** algorithm for unsupervised anomaly detection.
Isolation Forest is suitable because AWS data may not always have enough labeled examples of every possible fault.

Instead of requiring a large labeled dataset:

Normal Data
     ↓
Learn normal distribution
     ↓
Isolation Forest
     ↓
Identify unusual observations

Anomalous observations are easier to isolate because they are different from the majority of normal observations.

Why Isolation Forest?

| Requirement                    | Isolation Forest |
| ------------------------------ | ---------------- |
| Labeled data required          | ❌ No             |
| Suitable for anomaly detection | ✅                |
| Multivariate data              | ✅                |
| Computationally efficient      | ✅                |
| Suitable for large datasets    | ✅                |
| Easy to retrain                | ✅                |

🧮 Hybrid Anomaly Score
The final anomaly decision is not based solely on the ML model.
Conceptually:

Final Anomaly Score
        =
ML Score
+
Rule-Based Score
+
Temporal Score
+
Spatial/Consistency Score

The resulting score is mapped to a severity level.

This approach combines the adaptability of Machine Learning with the interpretability of domain rules.

🛠️ Technology Stack

Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Scikit-learn
* Joblib

Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Recharts
* Leaflet

Database

* PostgreSQL
* Supabase

Machine Learning

* Scikit-learn
* Isolation Forest
* Feature-based anomaly scoring

Deployment

* Render
* Supabase
* GitHub

📁 Project Structure

SkyGuard-AI/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── anomaly_service.py
│   │       ├── ml_engine.py
│   │       └── monitor.py
│   │
│   ├── data/
│   │   └── skyguard.db
│   │
│   ├── models/
│   │   └── isolation_forest.joblib
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── public/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   └── skyguard/
│   │   │       ├── network-map.tsx
│   │   │       └── trend-chart.tsx
│   │   │
│   │   ├── lib/
│   │   │   └── skyguard-api.ts
│   │   │
│   │   ├── routes/
│   │   │   ├── __root.tsx
│   │   │   └── index.tsx
│   │   │
│   │   ├── styles.css
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── .gitignore
├── render.yaml
└── README.md

⚙️ Installation
Prerequisites

Install the following:

* Python 3.10+
* Node.js 18+
* npm
* Git
* PostgreSQL/Supabase account

🔧 Backend Setup
Clone the repository:

bash
git clone https://github.com/<your-username>/SkyGuard-AI.git

cd SkyGuard-AI


Navigate to the backend:

bash
cd backend

Create a virtual environment:

bash
python -m venv venv


Activate it on Windows:

bash
venv\Scripts\activate


Activate it on Linux/macOS:

bash
source venv/bin/activate

Install dependencies:

bash
pip install -r requirements.txt

🔐 Environment Variables

Create a `.env` file inside the backend directory.

Example:

env
DATABASE_URL=your_database_connection_string

SKYGUARD_ADMIN_USERNAME=admin
SKYGUARD_ADMIN_PASSWORD=your_secure_password

CORS_ORIGINS=http://localhost:5173

> Never commit `.env` to GitHub.

Use `.env.example` to document required environment variables.

▶️ Run Backend

From the `backend` directory:

bash
python run.py

The API will be available at:

http://localhost:8000

FastAPI documentation:

http://localhost:8000/docs

💻 Frontend Setup

Open another terminal:

bash
cd frontend


Install dependencies:

bash
npm install

Start the development server:

bash
npm run dev

The frontend will normally be available at:
http://localhost:5173

🔌 API Architecture

The frontend communicates with the backend through REST APIs.

Example flow:

React Dashboard
       │
       │ HTTP Request
       ▼
FastAPI
       │
       ▼
Service Layer
       │
       ├── ML Engine
       ├── Anomaly Service
       └── Database
       │
       ▼
PostgreSQL


The API layer provides separation between:

* User interface
* Business logic
* Machine learning
* Database operations

🔒 Security
SkyGuard AI incorporates several security practices:

* Authentication for protected dashboard access
* Environment variables for secrets
* Password protection
* CORS configuration
* API-level validation
* Database abstraction through SQLAlchemy
* No hard-coded production credentials

Production deployments should additionally use:

* HTTPS
* Strong password policies
* Secret management
* Rate limiting
* Role-based access control
* Audit logging

📊 Dashboard

The dashboard provides a centralized view of AWS infrastructure.

Main components

┌───────────────────────────────────────────────┐
│              SKYGUARD AI                     │
├───────────────────────────────────────────────┤
│                                               │
│  Total Stations     Active Alerts   Health   │
│       XX                 XX           XX%     │
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


🚨 Example Anomaly Scenario
Suppose an AWS normally reports:

Temperature: 27°C
Pressure:    1012 hPa
Humidity:    65%


Suddenly the station reports:

Temperature: 91°C
Pressure:    1011 hPa
Humidity:    64%

SkyGuard AI evaluates:

Temperature deviation
        +
ML anomaly score
        +
Temporal change
        +
Other sensor consistency
        ↓
Potential Sensor Anomaly
        ↓
High Severity Alert

The operator can then investigate the affected station.

🎯 Advantages
Traditional Threshold System

Sensor → Threshold → Alert

SkyGuard AI

Sensor
  ↓
Validation
  ↓
Feature Analysis
  ↓
ML Detection
  +
Domain Rules
  +
Temporal Analysis
  +
Spatial Consistency
  ↓
Hybrid Score
  ↓
Severity
  ↓
Intelligent Alert

This reduces dependence on manually configured thresholds and provides additional context around detected anomalies.

📈 Future Enhancements
The architecture is designed to support future improvements.

Planned enhancements

* Real-time MQTT telemetry ingestion
* Advanced time-series models
* LSTM/Autoencoder-based anomaly detection
* Automated sensor fault classification
* SMS/email notifications
* Mobile application
* Offline edge-based anomaly detection
* Predictive maintenance
* Automated model retraining
* Advanced geospatial anomaly detection
* Role-based access control
* Historical anomaly analytics

🧪 Testing

The system can be tested using:
Normal telemetry

json
{
  "temperature": 28.5,
  "pressure": 1012.4,
  "humidity": 67.2
}

Abnormal telemetry

json
{
  "temperature": 89.7,
  "pressure": 1011.8,
  "humidity": 66.5
}

The anomaly engine evaluates the input and generates the corresponding anomaly score and severity.

📦 Deployment

Backend
The FastAPI backend can be deployed using Render.

Deployment configuration is provided through:
render.yaml

Database
Production data can be stored in Supabase PostgreSQL.

Frontend
The React/Vite frontend can be deployed using a static hosting platform.

🌐 Production Architecture
                    INTERNET
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
      React Frontend          AWS Stations
             │                     │
             │ REST API            │
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

🏆 SIH Relevance

SkyGuard AI addresses the need for intelligent monitoring of distributed weather-station infrastructure.
The solution focuses on:

*Automation
*Artificial Intelligence
*Anomaly Detection
*Real-Time Monitoring
*Sensor Reliability
*Data Quality
*Geospatial Visualization
*Scalable Cloud Architecture

The system can help monitoring teams identify potentially faulty or abnormal stations faster and provide a centralized view of the AWS network.

👥 Team
Team Name
[Elementalists]

Team Members

| Name       | Role                    |
| ---------- | ----------------------- |
| [Member 1] | Team Lead / Backend     |
| [Member 2] | AI/ML                   |
| [Member 3] | Frontend                |
| [Member 4] | Database / Cloud        |
| [Member 5] | Testing / Documentation |
| [Member 6] | Research / Integration  |

📜 License
This project is developed as part of the **Smart India Hackathon (SIH).
Add your preferred open-source license here if the project is intended for public distribution.

⭐ Acknowledgements

* Smart India Hackathon
* Open-source Python ecosystem
* FastAPI
* Scikit-learn
* React
* PostgreSQL
* Supabase
* OpenStreetMap / Leaflet ecosystem


📬 Contact
For project-related queries:

Team:[Elementalists]
Email:[lakshitha2005che@gmail.com]
GitHub:[https://github.com/lakshm22/SkyGuardAI-SIH2026]
