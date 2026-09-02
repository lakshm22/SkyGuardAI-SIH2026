# SkyGuard AI — Python Backend

FastAPI backend replacing the Streamlit layer for the SkyGuard AI React dashboard.

## Architecture

React/Vite UI → FastAPI REST API → Hybrid anomaly engine → SQLite
                                           ├─ Isolation Forest
                                           ├─ domain/physical checks
                                           ├─ temporal deviation
                                           ├─ spatial/neighbor consistency
                                           ├─ root-cause classification
                                           ├─ corrected-value estimation
                                           └─ sensor-health scoring

The SIH problem statement requires real-time detection using temperature, atmospheric
pressure and relative humidity, plus anomaly alerts, severity/confidence, root-cause
classification, dashboard visualization and sensor health. The supplied tech-stack
document recommends Python, Pandas/NumPy, scikit-learn/Isolation Forest, FastAPI,
SHAP, MQTT/simulated streaming and optional ESP32 deployment.

## 1. Create/activate your Conda environment

```powershell
conda activate skyguard
cd C:\path\to\SkyGuard_AI_Backend
```

## 2. Install packages

```powershell
pip install -r requirements.txt
```

## 3. Start API

```powershell
python run.py
```

API:
`http://localhost:8000`

Swagger:
`http://localhost:8000/docs`

## 4. Test a real reading

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/readings `
  -ContentType "application/json" `
  -Body '{"station_id":"AWS01","temperature":31.4,"pressure":1007.8,"humidity":71}'
```

## 5. Test the anomaly detector

This creates the reference-style extreme-temperature case:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/simulate `
  -ContentType "application/json" `
  -Body '{"station_id":"AWS01","anomaly_type":"temperature_spike"}'
```

## 6. Useful endpoints

- `GET /api/health`
- `GET /api/stations`
- `GET /api/stations/{station_id}`
- `POST /api/readings`
- `GET /api/stations/{station_id}/latest`
- `GET /api/stations/{station_id}/trend?hours=1`
- `GET /api/alerts`
- `PATCH /api/alerts/{alert_id}`
- `POST /api/simulate`
- `GET /api/dashboard/{station_id}`
- `GET /api/export/readings`
- `POST /api/model/retrain`

## React connection

Your React app should use:

```js
const API = "http://localhost:8000/api";
fetch(`${API}/dashboard/AWS01`);
```

Do not point React at Streamlit anymore. FastAPI becomes the backend/API layer.

## Important model note

The included Isolation Forest is a runnable MVP detector trained on a synthetic normal-weather distribution.
For the SIH final model, replace that baseline with the historical AWS dataset and injected-anomaly evaluation
pipeline. SHAP is included as a dependency, but feature attribution should be wired to the final fitted model
after the actual training dataset/model pipeline is fixed.
