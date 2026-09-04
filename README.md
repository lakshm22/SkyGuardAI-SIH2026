# SkyGuard AI — Real-Time AWS Anomaly Detection

SkyGuard AI is a React + FastAPI monitoring console for Automatic Weather Stations (AWS). It continuously ingests temperature, atmospheric pressure and relative humidity, evaluates telemetry with a hybrid Isolation Forest + domain/temporal/spatial detector, and produces operator alerts.

## What's included in this build

- Admin login and protected operator controls
- React/Vite dashboard with a redesigned mission-control UI
- Real geographical AWS map using Leaflet + OpenStreetMap
- Clickable station markers with coordinates, health and status
- Live dashboard polling every 3 seconds
- Backend continuous demo monitor that generates realistic telemetry and sends it through the same anomaly engine
- Real AWS ingestion endpoint: `POST /api/readings`
- Browser/toast anomaly notifications
- Add/remove AWS stations from the admin console
- Six deterministic anomaly demonstrations:
  - Temperature spike
  - Pressure shift
  - Humidity spike
  - Multi-parameter anomaly
  - Frozen sensor
  - Communication error
- PDF anomaly report export
- Admin-only model/simulation/management operations
- PostgreSQL support with an isolated `skyguard` schema so the project can share one Render PostgreSQL database with another application
- SQLite fallback for local development

## Architecture

```text
AWS / ESP32 / Simulator
        |
        v
POST /api/readings
        |
        v
Hybrid Anomaly Engine
  |       |       |
  |       |       +--> Spatial mismatch
  |       +----------> Temporal deviation / frozen values
  +------------------> Isolation Forest + domain rules
        |
        +--> Reading persisted
        +--> Station health updated
        +--> Alert created when anomaly is detected
        |
        v
FastAPI
        |
        +--> React dashboard (3-second polling)
        +--> Browser notifications
        +--> Geographic map
        +--> PDF reports
```

## PostgreSQL: sharing one Render database

Set:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
DB_SCHEMA=skyguard
```

The backend automatically creates the schema:

```sql
CREATE SCHEMA IF NOT EXISTS skyguard;
```

SkyGuard tables therefore live at:

```text
skyguard.stations
skyguard.readings
skyguard.alerts
```

Your other application can keep its own tables/schemas in the same PostgreSQL database.

For local development, omit `DATABASE_URL` and the backend falls back to:

```env
SKYGUARD_DB=sqlite:///./data/skyguard.db
```

## Admin credentials

Configure them in the backend environment:

```env
SKYGUARD_ADMIN_USERNAME=admin
SKYGUARD_ADMIN_PASSWORD=change-this-password
```

Do not commit real credentials.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python run.py
```

API: `http://localhost:8000`

### Frontend

From the project root:

```bash
npm install
npm run dev
```

The dashboard defaults to:

```text
http://localhost:5173
```

If the backend is hosted elsewhere, set:

```env
VITE_SKYGUARD_API_URL=https://your-api.example.com/api
```

## Live monitoring

The **Live Monitor** control on the dashboard starts a backend demo stream. Every configured station receives a realistic normal reading at the selected interval and the reading passes through the real anomaly-processing pipeline.

For actual hardware/AWS gateways, send telemetry to:

```http
POST /api/readings
Content-Type: application/json

{
  "station_id": "AWS01",
  "temperature": 31.2,
  "pressure": 1008.4,
  "humidity": 68.5
}
```

The dashboard automatically detects new alerts through its 3-second polling cycle.

## Demo anomalies

Open **Demo Anomaly Injection** after signing in.

Recommended SIH demo sequence:

1. Start Live Monitor.
2. Select `AWS01`.
3. Inject **Temperature spike**.
4. Show the alert toast/browser notification.
5. Show the anomaly score and root-cause explanation.
6. Show the station status on the geographical map.
7. Inject **Multi-parameter anomaly** to demonstrate a Critical event.
8. Resolve the alert from the Alert Feed.
9. Add another AWS station with real latitude/longitude.
10. Export the station's PDF report.

## Geographical map

The map uses Leaflet and OpenStreetMap tiles. Internet access is required for the map library CDN and map tiles. Station latitude/longitude values come from the database, so newly added stations appear at their actual coordinates.

## Render

The included `render.yaml` deploys the FastAPI backend. Supply your existing Render PostgreSQL connection string as `DATABASE_URL` and keep:

```env
DB_SCHEMA=skyguard
```

Also configure:

```env
SKYGUARD_ADMIN_USERNAME=...
SKYGUARD_ADMIN_PASSWORD=...
CORS_ORIGINS=https://your-frontend.example.com
```

If you use one Render PostgreSQL database for multiple applications, **do not change `DB_SCHEMA` away from `skyguard`** for this application unless you intentionally want to rename its tables' schema.
