# Connecting the existing React UI

Replace the demo/hardcoded data in `src/main.jsx` with API calls.

Base URL:
```js
const API = "http://localhost:8000/api";
```

For selected station:
```js
const res = await fetch(`${API}/dashboard/AWS01`);
const dashboard = await res.json();
```

Use:
- `dashboard.latest` for the metric cards
- `dashboard.trend` for the chart
- `dashboard.latest_alert` for the alert card
- `GET /api/stations` for the sidebar and map
- `GET /api/alerts` for anomaly history

To send a sensor reading:
```js
await fetch(`${API}/readings`, {
  method: "POST",
  headers: {"Content-Type":"application/json"},
  body: JSON.stringify({
    station_id:"AWS01",
    temperature:31.4,
    pressure:1007.8,
    humidity:71
  })
});
```

A production realtime UI should poll `/api/dashboard/{station_id}` every few seconds or use
a WebSocket layer. The current backend is intentionally REST-first so the MVP is easier to
debug during the hackathon.
